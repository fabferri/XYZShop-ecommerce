# Backup & Rebuild Guide

This guide explains how to safely back up the XYZShop database, delete it, and
rebuild the full demo dataset from scratch — without losing anything important.

---

## Can I delete `db.sqlite3` and start from scratch?

Yes. The demo dataset is fully reproducible from `exported_products.py` and the
utility scripts. Read the notes below first so you know exactly what is preserved,
regenerated, or lost.

### What gets fully rebuilt

- 9 categories, all 507 products, auto-generated descriptions, and 507
  price-history records — restored from [`exported_products.py`](exported_products.py)
  (currently in sync with the database).
- **Product images are NOT affected.** They live on disk in `media/products/`,
  not in `db.sqlite3`, so deleting the database leaves them untouched.

### What gets regenerated fresh (equivalent, but not identical records)

- 50 sample customers (password `customer123`), ~500 orders, ~375 reviews, and
  sale records are **randomly generated** on each run. You get an equivalent
  demo dataset, but specific order IDs, dates, and review text will differ.

### What you WOULD lose

Anything not captured in `exported_products.py` or the seed scripts, e.g.:

- Products added manually via the admin (the `add-new-products-manually/`
  workflow) since the last `export_products.py` run.
- Any real accounts / orders / reviews created during testing.
- A changed admin password — `create_admin.py` resets it to `admin` / `admin123`.

---

## Safe procedure (recommended)

Back up first, then rebuild:

```powershell
# 1. Activate the virtual environment
.venv\Scripts\Activate.ps1

# 2. Snapshot current products to exported_products.py (captures manual additions)
python export_products.py

# 3. Back up the current database file (belt-and-suspenders)
Copy-Item db.sqlite3 db.sqlite3.bak

# 4. Delete and rebuild
Remove-Item db.sqlite3
python manage.py migrate
python create_admin.py
python restore_database.py
```

---

## Quick procedure (demo data only)

If you have **only ever used the seeded demo data** (no manual product/user
changes), you can skip the backup steps and rebuild directly — you won't lose
anything meaningful:

```powershell
.venv\Scripts\Activate.ps1
Remove-Item db.sqlite3
python manage.py migrate
python create_admin.py
python restore_database.py
```

---

## Restoring from a backup

If you kept a `db.sqlite3.bak` and want to roll back:

```powershell
# Stop the server first, then:
Remove-Item db.sqlite3
Copy-Item db.sqlite3.bak db.sqlite3
```

Your `exported_products.py` snapshot can also be re-imported at any time with
`python restore_database.py`.

---

## Notes

- The default demo admin account is `admin` / `admin123`.
- Sample customer accounts use the password `customer123`.
- `restore_database.py` prompts for confirmation before deleting existing data
  when the database is not empty.
- See the main [`README.md`](README.md) "Database Setup" section for the full
  rebuild reference.
