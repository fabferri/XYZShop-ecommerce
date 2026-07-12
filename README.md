# XYZShop - Django E-Commerce Project

A Django-based e-commerce website for hardware and tools with 500+ products, where customers can browse and purchase products with full user authentication, order management, admin panel, and REST API.
The e-commerce website includes a warehouse management system.

## Table of Contents

- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Database Setup](#database-setup)
- [Resetting a User Password](#resetting-a-user-password)
- [Running the Project](#running-the-project)
  - [Development Server (WSGI)](#development-server-wsgi)
  - [Uvicorn (ASGI)](#uvicorn-asgi)
- [REST API](#rest-api)
- [Utility Scripts](#utility-scripts)
- [Models](#models)
- [URLs Reference](#urls-reference)

---

## Project Structure

```
XYZShop/
├── products/          # Product catalog and category management
│   ├── static/        # Product-specific static files
│   ├── templates/     # Product HTML templates
│   └── templatetags/  # Custom template tags
├── cart/              # Shopping cart functionality
├── orders/            # Order processing and management
├── accounts/          # User authentication and profile management
├── api/               # REST API (Django REST Framework)
│   ├── serializers.py # DRF serializers for all models
│   ├── views.py       # API views (generic + function-based)
│   ├── urls.py        # API URL routes under /api/
│   └── tests/         # 184 unit tests (split by feature)
│       ├── test_categories.py
│       ├── test_products.py
│       ├── test_reviews.py
│       ├── test_cart.py
│       ├── test_orders.py
│       ├── test_auth.py
│       └── test_e2e.py
├── xyz_store/         # Main project settings and configuration
├── media/             # Uploaded images and files
│   └── products/      # Product images 1024x1024
├── templates/         # HTML templates
├── add-new-products-manually/  # New product data to add manually
├── .venv/             # Virtual environment
├── .env.example       # Environment variable template (copy to .env)
├── .gitignore         # Git ignore rules (excludes .env, caches, etc.)
├── TODO.md            # Production-readiness architecture roadmap
└── manage.py          # Django management script
```

---

## Installation & Setup

The project is already set up in your virtual environment with Django 6.0.7 and Python 3.13.

### Prerequisites

- Python 3.13
- pip (Python package installer)
- Virtual environment (.venv)

### Initial Setup

1. Open a terminal and activate the virtual environment:
   ```bash
   .venv\Scripts\Activate.ps1
   ```

1. **Install Dependencies**:
   ```python
   pip install -r requirements.txt
   ```

The project dependencies are:
- **Django** 6.0.7
- **djangorestframework** 3.17.1
- **django-filter** 26.1
- **Pillow** 12.3.0
- **uvicorn[standard]** 0.51.0 — ASGI server for production deployment
- **whitenoise** 6.12.0 — static file serving for ASGI/WSGI
- **asgiref** 3.11.1
- **sqlparse** 0.5.5
- **tzdata** 2026.3

## Environment Configuration

Runtime configuration is read from environment variables (loaded from a `.env` file at the project root via `python-dotenv`). Copy the template and adjust the values:

```powershell
Copy-Item .env.example .env
```

### `.env.example` vs `.env`

`.env.example` is a **template** for environment configuration. It documents every variable the app reads, with placeholder/default values but **no real secrets**, so it is safe to commit to version control.

- **Template to copy** — `Copy-Item .env.example .env`, then edit `.env` with your real values.
- **`.env` is git-ignored** — the actual `.env` (real `SECRET_KEY`, etc.) is excluded by [`.gitignore`](.gitignore), so secrets are never committed.
- **Loaded at startup** — [`xyz_store/settings.py`](xyz_store/settings.py) calls `load_dotenv(BASE_DIR / '.env')` to read the variables into the environment.

In short: `.env.example` is the committed, secret-free blueprint; `.env` is your local, secret-filled copy that the app actually reads. It also serves as onboarding documentation — new contributors immediately see what needs configuring without reading the settings code.

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | insecure dev key | Django cryptographic key. **Set a strong random value in production.** |
| `DEBUG` | `True` | Set to `False` in production. |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hosts/domains the site may serve. |
| `CSRF_TRUSTED_ORIGINS` | *(empty)* | Comma-separated HTTPS origins trusted for CSRF. |
| `SECURE_SSL_REDIRECT` | `True` | Redirect HTTP→HTTPS (only applied when `DEBUG=False`). |
| `SECURE_HSTS_SECONDS` | `31536000` | HSTS max-age (only applied when `DEBUG=False`). |

When `DEBUG=False`, the project automatically enables HTTPS redirects, HSTS, secure session/CSRF cookies, and `SECURE_PROXY_SSL_HEADER` (for running behind a reverse proxy / load balancer). Generate a production secret key with:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Validate production readiness at any time with:

```powershell
python manage.py check --deploy
```

It's a read-only diagnostic — it changes nothing, just tells you what to fix before going live.

## Database Setup

The file **db.sqlite3** is missing from the project than the database must be created as the first step. Django automatically builds the database structure when you run migrations. The project includes utility scripts for database management.

### Creating Database from Scratch

1. Open a terminal and activate the virtual environment:

   ```bash
   .venv\Scripts\Activate.ps1
   ```

1. **Run migrations** to create database structure:

   ```powershell
   python manage.py migrate
   ```

   Migrations is required before creating users.

1. **Create a superuser** for admin access for the first time:
Django does not come with a default admin username or password. To access the Django admin panel, you must create a superuser manually. This ensures security and prevents unauthorized access.

   ```powershell
   python manage.py createsuperuser
   ```

   You will be prompted for:
   - Username
   - Email address
   - Password (hidden while typing, must meet Django’s password validation rules)

1. **Populate the database** with products, users, orders, product review:

   ```python
   python restore_database.py
   ```

   - Deletes all existing products, categories, orders, and sales
   - Imports product definitions from `exported_products.py`
   - Recreates all 507 products from exported data
   - load 408 online products (visible to customers)
   - load 99 products in the warehouse (visible to the admin only). The warehousing products are flagged with `is_online=False`
   - Includes all 9 categories: Electrical, Garden, Hand Tools, Outdoor, Paint & Decorating, Plumbing, Power Tools, Screws & Fixings, Sealants
   - Creates 50 sample customer accounts (password: `customer123`), ~500 orders with order items, sale records, and ~375 product reviews
   - **Product images**: All stored in `media/products/` folder (1024x1024 .jpg format, generated by DALL-E 3)

---

## Resetting a User Password

Django stores passwords in a hashed format, so you cannot view the old password — you must reset it. These methods work for **any user** (admin or regular customer).

### Method 1 – Using changepassword Command (quickest):
```
python manage.py changepassword <username>
```
Replace `<username>` with the target username, then enter and confirm the new password.

### Method 2 – Using Django Shell:
```
python manage.py shell

from django.contrib.auth.models import User
user = User.objects.get(username='<username>')  # Replace with target username
user.set_password('NewSecurePassword123!')
user.save()
```
Exit the shell with `exit()`. The user can now log in with the new password.

### Method 3 – List All Users (if username is forgotten):
```
python manage.py shell

from django.contrib.auth.models import User
for u in User.objects.all():
    print(f"{u.username:20s} {'(admin)' if u.is_superuser else '(customer)':12s} {u.email}")
```

### Method 4 – Create a New Superuser:
```
python manage.py createsuperuser
```

---

## Running the Project

### Development Server (WSGI)

1. **Start the development server**:

   In virtual environment  (.venv\Scripts\Activate.ps1)

   ```python
   python manage.py runserver
   ```

1. **Access the site**:
   - **Main Store**: <http://127.0.0.1:8000/>
   - **Admin Panel**: <http://127.0.0.1:8000/admin/>
   - **Shopping Cart**: <http://127.0.0.1:8000/cart/>
   - **REST API Root**: <http://127.0.0.1:8000/api/>

### Uvicorn (ASGI)

The project is configured to run with **uvicorn**, a high-performance ASGI server suitable for production deployment.

1. **Development** (with auto-reload):

   ```powershell
   uvicorn xyz_store.asgi:application --host 127.0.0.1 --port 8000 --reload
   ```

2. **Production** (multi-worker):

   ```powershell
   uvicorn xyz_store.asgi:application --host 0.0.0.0 --port 8000 --workers 4
   ```

The ASGI configuration is in `xyz_store/asgi.py`. All views are synchronous and Django automatically wraps them in threads when served via ASGI, so no code changes are required.

**Static files**: WhiteNoise middleware serves static files (admin CSS/JS, DRF assets) directly from the application. The setting `WHITENOISE_USE_FINDERS = True` lets WhiteNoise find files from source directories automatically — no `collectstatic` step is needed during development.

For production, you can disable `WHITENOISE_USE_FINDERS` and run `collectstatic` instead for better performance (pre-compressed gzip/brotli files, immutable cache headers, single dictionary lookup per request):
```powershell
python manage.py collectstatic --noinput
```
This command copies all static files from every app (`django.contrib.admin`, `rest_framework`, `products/static/`, etc.) into a single `staticfiles/` directory (`STATIC_ROOT`). WhiteNoise then builds an in-memory index at startup and serves files from there without scanning directories on each request. The `--noinput` flag skips the confirmation prompt.

### Docker

The project ships with a `Dockerfile`, `docker-entrypoint.sh`, `.dockerignore`, and `docker-compose.yml` for running in containers. The image installs dependencies, runs `collectstatic`, applies migrations on startup, runs as a non-root user, and serves the app with Uvicorn (4 workers).

> For full details — configuration, data persistence, running management commands, and troubleshooting — see [README-docker.md](README-docker.md).

**Using Docker Compose** (recommended for local runs):

```powershell
docker compose up --build
```

Then open <http://localhost:8000/>. The SQLite database (`db.sqlite3`) and `media/` folder are bind-mounted to the host so data persists across restarts.

**Using plain Docker**:

```powershell
# Build the image
docker build -t xyzshop .

# Run the container
docker run -p 8000:8000 xyzshop
```

For production, set `DEBUG=False`, a strong `SECRET_KEY`, and the correct `ALLOWED_HOSTS` (via `environment:` in `docker-compose.yml`, an `env_file`, or `-e` flags) and move to PostgreSQL for the database (see [`TODO.md`](TODO.md)).

---

## REST API

The project includes a full REST API built with **Django REST Framework** under the `/api/` prefix. All endpoints return JSON. The existing template-based views remain unchanged.

### Authentication

The API supports two authentication methods:
- **Session authentication** — works with browser cookies (same as the main site)
- **Token authentication** — use `Authorization: Token <key>` header for API clients

Obtain a token via `/api/auth/register/` or `/api/auth/login/`.

### Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/categories/` | No | List all categories with product counts |
| GET | `/api/products/` | No | List products (supports `?search=`, `?category__slug=`, `?ordering=price`) |
| GET | `/api/products/{id}/` | No | Product detail with reviews |
| GET | `/api/products/{id}/reviews/` | No | List reviews for a product |
| POST | `/api/products/{id}/reviews/create/` | Yes | Submit a review (one per user per product) |
| GET | `/api/cart/` | No | View current session cart |
| POST | `/api/cart/add/` | No | Add item `{product_id, quantity}` |
| POST | `/api/cart/remove/{id}/` | No | Remove item from cart |
| POST | `/api/cart/clear/` | No | Clear entire cart |
| GET | `/api/orders/` | Yes | List authenticated user's orders |
| GET | `/api/orders/{id}/` | Yes | Order detail (own orders only) |
| POST | `/api/orders/create/` | Yes | Create order from current cart |
| POST | `/api/auth/register/` | No | Register new user, returns token |
| POST | `/api/auth/login/` | No | Login, returns token |
| GET | `/api/auth/profile/` | Yes | Authenticated user's profile |

### Product Filtering & Search

```bash
# Search by name or description
GET /api/products/?search=hammer

# Filter by category
GET /api/products/?category__slug=power-tools

# Order by price (ascending or descending)
GET /api/products/?ordering=price
GET /api/products/?ordering=-price
```

### Example: Token Workflow

```bash
# Register and get token
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
# Response: {"token": "abc123...", "user": {...}}

# Use token for protected endpoints
curl http://127.0.0.1:8000/api/orders/ \
  -H "Authorization: Token abc123..."
```

### Running API Tests

```powershell
# Run all 184 API tests
python manage.py test api --verbosity=2

# Run tests for a specific area
python manage.py test api.tests.test_products
python manage.py test api.tests.test_cart
python manage.py test api.tests.test_orders
python manage.py test api.tests.test_reviews
python manage.py test api.tests.test_auth
python manage.py test api.tests.test_categories
python manage.py test api.tests.test_e2e

# Run the template-based order/checkout tests
python manage.py test orders

# Run the whole suite (196 tests)
python manage.py test api orders
```

The API test suite includes **184 tests** covering all endpoints, edge cases, validation, auth, and end-to-end flows. The `orders` app adds template-level checkout and payment tests, including stock-decrement and insufficient-stock rollback (**196 tests** total).

---


## Models



### Product
- **Category**: ForeignKey to Category
- **Name**: Product name (max 200 characters)
- **Slug**: URL-friendly identifier (auto-generated)
- **Image**: Product image file
- **Description**: Detailed product description (optional)
- **Price**: Decimal field (10 digits, 2 decimal places)
- **Cost Price**: Purchase cost (optional, for margins)
- **Stock**: Integer for available quantity
- **Available**: Boolean for visibility
- **Is Online**: Boolean for warehouse status
- **Created**: Auto timestamp on creation
- **Updated**: Auto timestamp on modification

### ProductPriceHistory
- **Product**: ForeignKey to Product (related_name='price_history')
- **Cost Price**: Historical cost price at time of change
- **Selling Price**: Historical selling price at time of change
- **Changed By**: ForeignKey to User (optional, who made the change)
- **Changed At**: Timestamp of when the price was changed
- **Reason**: Optional text field for reason of price change
- **Calculated Fields**: Margin percentage and profit

**Features**:
- Automatic tracking via Django signals (no manual intervention needed)
- Complete audit trail of all price changes
- Color-coded margin display in admin (green=high, red=loss)
- Read-only to ensure data integrity
- Indexed for fast queries

### ProductReview
- **Product**: ForeignKey to Product (related_name='reviews')
- **User**: ForeignKey to User (who wrote the review)
- **Rating**: Integer field (1-5 stars)
- **Title**: Review title (max 200 characters)
- **Comment**: Review text content
- **Verified Purchase**: Boolean indicating if user purchased the product
- **Created**: Auto timestamp on creation
- **Updated**: Auto timestamp on modification

**Features**:
- One review per user per product (unique_together constraint)
- Visual star rating display (★★★★★)
- Display on product detail pages with rating summary
- Rating distribution calculation
- Verified purchase badge for authenticated purchases

### Category
- **Name**: Category name (max 200 characters, unique)
- **Slug**: URL-friendly identifier (unique, auto-generated)

### Order
- **User**: ForeignKey to User (optional, nullable for guest orders)
- **First Name**: Customer first name
- **Last Name**: Customer last name
- **Email**: Customer email
- **Address**: Delivery address
- **Postal Code**: Delivery postal code
- **City**: Delivery city
- **Created**: Auto timestamp on creation
- **Updated**: Auto timestamp on modification
- **Paid**: Boolean for payment status
- **Payment Method**: Choice field (card / paypal / bank / cash, default 'card')
- **Payment ID**: Transaction reference (optional, set after payment)
- **Status**: Choice field (pending / processing / shipped / delivered / cancelled, default 'pending')
- **Methods**: `get_total_cost()` — sum of all order item costs

**Features**:
- Order creation runs inside a database transaction: product rows are locked (`select_for_update`), stock is validated, and `Product.stock` is decremented atomically (`F('stock') - quantity`).
- If any item has insufficient stock, the whole order is rolled back — no partial orders. The template checkout redirects back to the cart; the API returns HTTP 400.

### OrderItem
- **Order**: ForeignKey to Order (related_name='items')
- **Product**: ForeignKey to Product (related_name='order_items')
- **Price**: Decimal field (price at time of order)
- **Quantity**: Integer for number of items
- **Methods**: `get_cost()` — `price * quantity`

### Sale
- **Order**: ForeignKey to Order (related_name='sales', nullable)
- **Date**: Auto timestamp when the sale was recorded
- **Category**: ForeignKey to Category
- **Item**: ForeignKey to Product
- **Sold Price**: Decimal field (price the item sold for)
- **Quantity**: Integer for number of items sold
- **Methods**: `get_total_amount()` — `sold_price * quantity`

**Features**:
- Created automatically via Django signal when an order is marked paid
- Powers the admin dashboard revenue and sales statistics

---

## URLs Reference

### Customer URLs
- **Home / All Products**: `/` or http://127.0.0.1:8000/
- **Category**: `/<category-slug>/` (e.g. `/power-tools/`)
- **Product Detail**: `/<id>/<slug>/` (e.g. `/762/air-compressor-50l-25hp/`)
- **Search**: `/search/?q=<query>`
- **Cart**: `/cart/`
- **Add to Cart**: `/cart/add/<product_id>/` (POST)
- **Remove from Cart**: `/cart/remove/<product_id>/` (POST)
- **Checkout**: `/orders/create/`
- **Payment**: `/orders/payment/<order_id>/`
- **Payment Done**: `/orders/payment-done/<order_id>/`
- **Register**: `/accounts/register/`
- **Login**: `/accounts/login/`
- **Logout**: `/accounts/logout/`
- **Profile**: `/accounts/profile/`
- **Order History**: `/accounts/orders/`

### REST API URLs
- **Categories**: `/api/categories/`
- **Products**: `/api/products/`
- **Product Detail**: `/api/products/<id>/`
- **Reviews**: `/api/products/<id>/reviews/`
- **Cart**: `/api/cart/`
- **Orders**: `/api/orders/`
- **Auth**: `/api/auth/register/`, `/api/auth/login/`, `/api/auth/profile/`

### Admin URLs
- **Admin Dashboard**: `/admin/`
- **Products**: `/admin/products/product/`
- **Categories**: `/admin/products/category/`
- **Orders**: `/admin/orders/order/`
- **Order Items**: `/admin/orders/orderitem/`
- **Users**: `/admin/auth/user/`

---

---

## Add manually new products

The folder **add-new-products-manually** contains a list of product pictures and product description to add manually the products after the database has been created and the website is running. Add the products with adminsitrator account.

## Utility Scripts

The project includes utility scripts for database management and maintenance:


### restore_database.py

**Purpose**: Restores the complete demo dataset from `exported_products.py`

**What it does**:
- Deletes all existing products, categories, orders, reviews, price history, and sales (superusers preserved; prompts for confirmation if data exists)
- Recreates 9 categories and 507 products (408 online + 99 warehouse)
- Auto-generates product descriptions and 507 price history records
- Creates 50 sample customers (password: `customer123`)
- Creates ~500 orders with order items, sale records, and ~375 product reviews

**When to use**:
- Rebuilding the full demo database from scratch
- After `python manage.py migrate` and `python create_admin.py`

### export_products.py

**Purpose**: Exports all current product definitions from database

**What it does**:
- Queries all products and categories from database
- Generates Python code with CATEGORIES and ALL_PRODUCTS dictionaries
- Saves to `exported_products.py` file
- Preserves all product attributes including online/warehouse status

**When to use**:
- Creating backup of current product data
- Before making major changes to database
- Sharing product catalog structure

### db_populate_fresh_database.py

**Purpose**: Populates database with products marked as warehouse (not online)

**What it does**:
- Deletes all existing products and categories
- Creates 4 sample categories
- Creates products with `is_online=False` (warehouse status)
- Useful for testing warehouse functionality

**When to use**:
- Testing warehouse product management
- Creating test environment with warehouse-only products
- Development and testing scenarios

### db_delete_all_records.py

**Purpose**: Deletes all database records (except superusers)

**What it does**:
- Deletes all Sales records
- Deletes all OrderItems
- Deletes all Orders
- Deletes all Products
- Deletes all Categories
- Deletes all non-superuser Users
- Preserves superuser accounts for admin access

**When to use**:
- Starting completely fresh
- Clearing test data
- Before importing new data

**Warning**: This is destructive! All data will be lost (except superusers).

### extract_product_images.py

**Purpose**: Lists all product images from media folder

**What it does**:
- Scans `media/products/` directory
- Lists all image files (.jpg, .png, .gif)
- Saves list to `product_images_list.txt`

**When to use**:
- Auditing product images
- Checking which images exist
- Before bulk operations on images

### compare_product_images.py

**Purpose**: Compares actual images with stored list

**What it does**:
- Reads `product_images_list.txt`
- Compares with actual files in `media/products/`
- Identifies missing images
- Identifies extra images not in list

**When to use**:
- Finding missing product images
- Identifying orphaned image files
- Verifying image integrity

### create_admin.py

**Purpose**: Creates a superuser account programmatically

**What it does**:
- Creates superuser with predefined credentials
- Username: admin
- Password: admin123

**When to use**:
- Quick admin account creation
- Automated setup scripts

### set_existing_products_online.py

**Purpose**: Sets all products to online status

**What it does**:
- Updates all products to `is_online=True`
- Makes all warehouse products visible to customers

**When to use**:
- Bulk publishing warehouse products
- Making entire catalog visible

### Workflow Examples

**Complete Fresh Setup** (when `db.sqlite3` is deleted or missing):
```powershell
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1

# 2. Create database structure (creates db.sqlite3 with all tables)
python manage.py migrate

# 3. Create admin account (admin / admin123)
python create_admin.py

# 4. Populate with full demo dataset (products, customers, orders, reviews, sales)
python restore_database.py
```

**Backup Current Data**:

```powershell
# Export current products
python export_products.py

# Copy exported file for safekeeping
Copy-Item exported_products.py exported_products_backup.py
```

**Reset to Original State** (keeps `db.sqlite3`, wipes all data, then restores):

```powershell
# Step 1: Delete ALL records (sales, orders, reviews, price history, products, categories, ALL users including superusers)
# WARNING: prompts for confirmation — type "yes" to proceed
python db_delete_all_records.py

# Step 2: Recreate the admin account (required because Step 1 deletes all users)
python create_admin.py

# Step 3: Restore the full demo dataset (products, customers, orders, reviews, sales)
python restore_database.py
```

Unlike "Complete Fresh Setup", this does **not** delete `db.sqlite3` or re-run migrations — it only clears and repopulates the data.

`Tags: Django, Django REST Framework, REST API` <br>
`date: 15-12-2025` <br>
`last updated: 12-07-2026` <br>