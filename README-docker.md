# Running XYZShop in Docker

This guide explains how to build and run the XYZShop Django e-commerce
application in Docker containers. It covers the provided Docker files, quick
start commands, configuration, data persistence, and common operations.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Files Overview](#docker-files-overview)
- [Quick Start](#quick-start)
  - [Option A: Docker Compose (recommended)](#option-a-docker-compose-recommended)
  - [Option B: Plain Docker](#option-b-plain-docker)
- [What Happens on Startup](#what-happens-on-startup)
- [Configuration (Environment Variables)](#configuration-environment-variables)
- [Data Persistence](#data-persistence)
- [Common Operations](#common-operations)
- [Production Notes](#production-notes)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Docker Desktop** (Windows/macOS) or **Docker Engine** + **Docker Compose** (Linux).
- Verify the installation:

  ```powershell
  docker --version
  docker compose version
  ```

---

## Docker Files Overview

| File | Purpose |
|------|---------|
| `Dockerfile` | Builds the application image (Python 3.13-slim, installs dependencies, runs `collectstatic`, runs as a non-root user, serves via Uvicorn). |
| `docker-entrypoint.sh` | Container entrypoint: applies database migrations on startup, then launches the server. |
| `.dockerignore` | Excludes `.venv`, caches, `.git`, `.env`, `staticfiles/`, etc. from the build context. |
| `docker-compose.yml` | Convenience orchestration for local runs, with port mapping, environment variables, and volume mounts. |

---

## Quick Start

### Option A: Docker Compose (recommended)

Build and start the app with a single command from the project root:

```powershell
docker compose up --build
```

Then open the site:

- **Main Store**: <http://localhost:8000/>
- **Admin Panel**: <http://localhost:8000/admin/> (default demo admin: `admin` / `admin123`)
- **REST API Root**: <http://localhost:8000/api/>

Stop the app with `Ctrl+C`, or run it in the background:

```powershell
# Start detached
docker compose up --build -d

# View logs
docker compose logs -f

# Stop and remove the containers
docker compose down
```

### Option B: Plain Docker

Build the image and run a container manually:

```powershell
# Build the image (tag it "xyzshop")
docker build -t xyzshop .

# Run the container, mapping host port 8000 to the container
docker run -p 8000:8000 xyzshop
```

Run detached and manage the container:

```powershell
docker run -d -p 8000:8000 --name xyzshop xyzshop
docker logs -f xyzshop
docker stop xyzshop
docker rm xyzshop
```

---

## What Happens on Startup

When the container starts, `docker-entrypoint.sh` runs:

1. **`python manage.py migrate --noinput`** — applies any pending database migrations.
2. **`exec "$@"`** — launches the command from the Dockerfile `CMD`:

   ```
   uvicorn xyz_store.asgi:application --host 0.0.0.0 --port 8000 --workers 4
   ```

Static files are already collected during the image build (`collectstatic`), and
WhiteNoise serves them from within the container — no external web server is required.

---

## Configuration (Environment Variables)

The app reads configuration from environment variables (see `env.md` and
`.env.example`). In Docker you can provide them in three ways:

**1. Inline in `docker-compose.yml`:**

```yaml
    environment:
      DEBUG: "False"
      SECRET_KEY: "your-strong-random-key"
      ALLOWED_HOSTS: "shop.example.com,www.example.com"
```

**2. From a `.env` file** (uncomment `env_file` in `docker-compose.yml`):

```yaml
    env_file:
      - .env
```

**3. With `-e` flags on plain `docker run`:**

```powershell
docker run -p 8000:8000 `
  -e DEBUG=False `
  -e SECRET_KEY=your-strong-random-key `
  -e ALLOWED_HOSTS=shop.example.com `
  xyzshop
```

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | insecure dev key | Django cryptographic key. **Set a strong value in production.** |
| `DEBUG` | `True` | Set to `False` in production. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hosts/domains the site may serve. |
| `CSRF_TRUSTED_ORIGINS` | *(empty)* | Comma-separated HTTPS origins trusted for CSRF. |
| `SECURE_SSL_REDIRECT` | `True` | Redirect HTTP->HTTPS (only when `DEBUG=False`). |
| `SECURE_HSTS_SECONDS` | `31536000` | HSTS max-age (only when `DEBUG=False`). |

---

## Data Persistence

By default the app uses **SQLite** (`db.sqlite3`) and stores uploaded images in
`media/`. In `docker-compose.yml`, these are bind-mounted to the host so data
survives container restarts:

```yaml
    volumes:
      - ./db.sqlite3:/app/db.sqlite3
      - ./media:/app/media
```

- Without these mounts, changes made inside the container are lost when the
  container is removed.
- For real production workloads, move to **PostgreSQL** (see `TODO.md`, item 2);
  SQLite is not suitable for concurrent production traffic.

---

## Common Operations

Run management commands inside a running Compose service:

```powershell
# Open a shell in the running container
docker compose exec web sh

# Create a superuser
docker compose exec web python manage.py createsuperuser

# Run the test suite
docker compose exec web python manage.py test api orders

# Restore the full demo dataset
docker compose exec web python restore_database.py
```

With plain Docker, replace `docker compose exec web` with `docker exec -it xyzshop`.

---

## Production Notes

- Set `DEBUG=False`, a strong `SECRET_KEY`, and the correct `ALLOWED_HOSTS`.
  When `DEBUG=False`, the app automatically enables HTTPS redirect, HSTS, secure
  cookies, and `SECURE_PROXY_SSL_HEADER` (for running behind a reverse proxy).
- Validate readiness inside the container:

  ```powershell
  docker compose exec web python manage.py check --deploy
  ```

- Terminate TLS at a reverse proxy / load balancer (nginx, Azure App Service,
  etc.) in front of the container.
- Use a managed database (PostgreSQL) and object storage for media in production.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---------|--------------------|
| `port is already allocated` | Another process uses port 8000. Map a different host port: `-p 8080:8000` (or change the compose `ports`). |
| `DisallowedHost` error | Add your host/domain to `ALLOWED_HOSTS`. |
| Static files missing / unstyled admin | Rebuild the image so `collectstatic` runs: `docker compose up --build`. |
| Database changes lost after `down` | Ensure the `db.sqlite3` volume mount is present (see [Data Persistence](#data-persistence)). |
| Permission denied on `db.sqlite3` | The container runs as UID 1000; ensure the host file is writable by that user, or run migrations to recreate it. |
| Large image / slow build | The `media/` product images are large; the first build takes longer. Subsequent builds use the layer cache. |
