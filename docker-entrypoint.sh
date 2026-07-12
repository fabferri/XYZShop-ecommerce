#!/bin/sh
# Container entrypoint: apply database migrations, then start the app.
set -e

# Apply any pending database migrations.
python manage.py migrate --noinput

# Execute the container command (uvicorn by default; see Dockerfile CMD).
exec "$@"
