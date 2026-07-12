# XYZShop - Django e-commerce application
# Production-oriented image that runs the app via Uvicorn (ASGI).

FROM python:3.13-slim

# Keep Python lean and predictable inside the container.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System build dependencies (needed to build Pillow and similar wheels).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the application source.
COPY . .

# Collect static files so WhiteNoise can serve them from the container.
RUN python manage.py collectstatic --noinput

# Make the entrypoint executable and run as a non-root user for security.
RUN chmod +x /app/docker-entrypoint.sh \
    && useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# The entrypoint applies migrations, then execs the CMD below.
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "xyz_store.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
