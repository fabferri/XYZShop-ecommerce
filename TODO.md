# Architecture Improvements — Production Readiness

This document tracks the architectural changes required to take XYZShop from a
development/demo configuration to a production-ready deployment. Items are
grouped by priority. Status legend: [DONE] · [TODO].

---

## Critical (deployment blockers)

### 1. [DONE] Externalize secrets and config
- **Done.** `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`
  are read from environment variables (via `python-dotenv`) in
  [`xyz_store/settings.py`](xyz_store/settings.py). Template in
  [`.env.example`](.env.example); `.env` is git-ignored.
- Production security settings (SSL redirect, HSTS, secure cookies,
  `SECURE_PROXY_SSL_HEADER`) auto-activate when `DEBUG=False`.
- **Remaining:** generate and set a strong `SECRET_KEY` per environment; verify
  with `python manage.py check --deploy`.

### 2. [TODO] Move from SQLite to PostgreSQL
- SQLite is single-writer and file-locked — it will not handle concurrent
  production traffic.
- Switch `DATABASES` to PostgreSQL (e.g. via `dj-database-url` + `DATABASE_URL`
  env var). Add `psycopg[binary]` to `requirements.txt`.
- Note: this also makes the `select_for_update()` row-locking in the order flow
  effective (it is a no-op on SQLite).

### 3. [TODO] Integrate a real payment gateway
- [`orders/views.py`](orders/views.py) `payment()` currently simulates
  success and generates a fake `payment_id` via `uuid`.
- Integrate Stripe/PayPal, confirm payment via server-side webhook before
  setting `paid=True`, and never trust client-submitted card data.

### 4. [DONE] Transactional stock decrement
- **Done.** Both the template checkout ([`orders/views.py`](orders/views.py))
  and the API order flow ([`api/views.py`](api/views.py)) now wrap order
  creation in `transaction.atomic()`, lock product rows with
  `select_for_update()`, validate stock, and decrement atomically with
  `F('stock') - qty`. Insufficient stock rolls the whole order back.
- Covered by tests in [`api/tests/test_orders.py`](api/tests/test_orders.py)
  and [`orders/tests.py`](orders/tests.py).

---

## High

### 5. [TODO] Media file storage
- Uploaded product images live on local disk (`MEDIA_ROOT`), which breaks across
  multiple instances and is lost on redeploy.
- Use object storage (Azure Blob Storage / AWS S3) via `django-storages`.

### 6. [TODO] API rate limiting / throttling
- DRF default permission is `AllowAny` with no throttles.
- Add `DEFAULT_THROTTLE_CLASSES` / `DEFAULT_THROTTLE_RATES`, especially for
  `api/auth/login/` and `api/auth/register/` to prevent brute-force/abuse.

### 7. [TODO] Logging and error monitoring
- No `LOGGING` configuration exists.
- Add structured logging and an error-tracking service (Sentry / Azure
  Application Insights).

---

## Medium

### 8. [TODO] Caching and session backend
- Add a `CACHES` backend (Redis) and consider Redis-backed sessions for the
  session cart across workers.
- Cache category/product listings to reduce DB load.

### 9. [TODO] Remove redundant admin site
- Both [`xyz_store/admin.py`](xyz_store/admin.py) and
  [`xyz_store/custom_admin.py`](xyz_store/custom_admin.py) define a
  `CustomAdminSite`; only one is wired up. Delete the unused module.

### 10. [TODO] Convert root utility scripts to management commands
- DB-mutating scripts in the project root (`restore_database.py`,
  `set_cost_prices.py`, `set_existing_products_online.py`, etc.) should become
  Django management commands under `products/management/commands/` so they run
  inside the app registry and are testable/discoverable.

### 11. [TODO] Health check endpoint
- Add a lightweight `/healthz/` endpoint for load-balancer / container probes.

### 12. [TODO] Expand non-API test coverage
- The API has 184 tests, but template views, models, signals, and the `Cart`
  class need direct tests (order/payment template tests were added in item 4).

---

## Deployment / DevOps

### 13. [TODO] Production server and static files
- Run under a process manager (e.g. `gunicorn` with
  `uvicorn.workers.UvicornWorker`, multiple workers) behind nginx / Azure App
  Service.
- Disable `WHITENOISE_USE_FINDERS` and run `collectstatic` for production.

### 14. [TODO] Containerization and CI
- **Docker: done.** [`Dockerfile`](Dockerfile), [`docker-entrypoint.sh`](docker-entrypoint.sh),
  [`.dockerignore`](.dockerignore), and [`docker-compose.yml`](docker-compose.yml)
  build and run the app via Uvicorn (migrations applied on start, non-root user,
  static files collected).
- **Remaining:** add a CI pipeline that runs `manage.py check --deploy`,
  applies migrations, and executes the full test suite on every change.

---

## Summary

| # | Improvement | Priority | Status |
|---|-------------|----------|--------|
| 1 | Externalize secrets/config | Critical | Done |
| 2 | PostgreSQL | Critical | Pending |
| 3 | Real payment gateway | Critical | Pending |
| 4 | Transactional stock decrement | Critical | Done |
| 5 | Object storage for media | High | Pending |
| 6 | API throttling | High | Pending |
| 7 | Logging / monitoring | High | Pending |
| 8 | Caching / Redis sessions | Medium | Pending |
| 9 | Remove redundant admin site | Medium | Pending |
| 10 | Scripts → management commands | Medium | Pending |
| 11 | Health check endpoint | Medium | Pending |
| 12 | Expand non-API tests | Medium | Pending |
| 13 | Production server / static | Deployment | Pending |
| 14 | Docker + CI | Deployment | Partial (Docker done, CI pending) |
