# Environment Configuration Guide

This document explains how XYZShop reads its runtime configuration, the role of
`.env` / `.env.example`, and why the project works without a `.env` file. It is
intended for administrators and new contributors.

---

## TL;DR

- `.env` is **optional**. The app runs with zero configuration in development
  because every setting has a safe built-in default.
- `.env.example` is a **committed, secret-free template**. Copy it to `.env` and
  fill in real values when you need to override the defaults (e.g. production).
- `.env` is **git-ignored** (see [`.gitignore`](.gitignore)) so real secrets are
  never committed.

---

## Why there is no `.env` file in the repository

The absence of `.env` is intentional:

1. **It is git-ignored.** `.env` is meant to hold real secrets (`SECRET_KEY`,
   etc.). Committing it would leak them, so it never ships with the repo. Only
   the secret-free template `.env.example` is committed.
2. **The app runs fine without it.** Development works out of the box with no
   configuration, thanks to fallback defaults in
   [`xyz_store/settings.py`](xyz_store/settings.py).
3. **You create it only to override defaults** (production, or custom local
   settings).

---

## How the app works without `.env`

### 1. Loading `.env` is a no-op when the file is missing

```python
load_dotenv(BASE_DIR / '.env')
```

`load_dotenv()` simply returns `False` and sets nothing when there is no `.env`;
it does not raise an error.

### 2. Every variable is read with a default

```python
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-...')  # dev fallback
DEBUG = _env_bool('DEBUG', True)                                   # defaults to True
ALLOWED_HOSTS = _env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1')  # dev hosts
CSRF_TRUSTED_ORIGINS = _env_list('CSRF_TRUSTED_ORIGINS')           # empty
```

### 3. Resolution order

For any setting, the value is resolved in this order:

```text
OS environment variable  ->  value in .env  ->  hardcoded default in settings.py
```

Without a `.env`, the hardcoded default always wins, giving a fully working
development configuration.

---

## `.env.example` vs `.env`

| File | Committed? | Contains secrets? | Purpose |
|------|-----------|-------------------|---------|
| `.env.example` | Yes | No (placeholders only) | Template + documentation of every variable |
| `.env` | No (git-ignored) | Yes | Your local/production copy that the app actually reads |

Workflow:

```powershell
# 1. Create your local copy from the template
Copy-Item .env.example .env

# 2. Edit .env with real values (never commit it)
```

`.env.example` also serves as onboarding documentation — new contributors
immediately see what needs configuring without reading the settings code.

---

## Configuration variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | insecure dev key | Django cryptographic key. **Set a strong random value in production.** |
| `DEBUG` | `True` | Set to `False` in production. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hosts/domains the site may serve. |
| `CSRF_TRUSTED_ORIGINS` | *(empty)* | Comma-separated HTTPS origins trusted for CSRF. |
| `SECURE_SSL_REDIRECT` | `True` | Redirect HTTP->HTTPS (only applied when `DEBUG=False`). |
| `SECURE_HSTS_SECONDS` | `31536000` | HSTS max-age (only applied when `DEBUG=False`). |

---

## Production notes

When `DEBUG=False`, the project automatically enables:

- HTTPS redirect (`SECURE_SSL_REDIRECT`)
- HTTP Strict Transport Security (`SECURE_HSTS_SECONDS`, subdomains, preload)
- Secure session and CSRF cookies (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)
- `SECURE_PROXY_SSL_HEADER` (for running behind a reverse proxy / load balancer)

Generate a production secret key:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Validate production readiness at any time:

```powershell
python manage.py check --deploy
```

### Alternative: real environment variables

You can skip the `.env` file entirely and export real OS environment variables
instead (common in Docker, CI, or Azure App Service). `.env` is just a
convenient local way to supply the same variables.
