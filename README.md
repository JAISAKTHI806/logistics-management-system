# Logistics Management System

A Flask web app for a Software Engineering course project. It demonstrates customer orders, warehouse preparation, delivery assignment, shipment tracking, and role-based access for five user types.

## Run locally on Windows

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
py app.py
```

Open `http://127.0.0.1:5000`.

Local demo accounts:

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123` |
| Customer | `customer` | `cust123` |
| Dispatcher | `dispatcher` | `disp123` |
| Delivery agent | `agent` | `agent123` |
| Warehouse staff | `warehouse` | `ware123` |

Local development uses SQLite. The database is created under `instance/` and is excluded from Git.

## Deploy on Vercel

Vercel detects the Flask application from `app.py`. Static files are served from `public/static/`. Vercel runs the app as a serverless function, so use a hosted PostgreSQL database for persistent orders and users; SQLite files in a function are not persistent.

1. Push this project to a GitHub repository and import that repository at [vercel.com/new](https://vercel.com/new).
2. Create a PostgreSQL database with a provider such as Supabase or Neon, then copy its connection URL.
3. In the Vercel project settings, add these environment variables for Production (and Preview if needed):
   - `DATABASE_URL`: PostgreSQL connection URL.
   - `SECRET_KEY`: a long, unique random value.
   - `SEED_DEMO_DATA`: `true` to create the five demo roles on an empty database.
   - `DEMO_ADMIN_PASSWORD`, `DEMO_CUSTOMER_PASSWORD`, `DEMO_DISPATCHER_PASSWORD`, `DEMO_AGENT_PASSWORD`, `DEMO_WAREHOUSE_PASSWORD`: set a unique password for each demo account. Demo passwords are required before a new production database is seeded.
4. Redeploy after saving the environment variables. The login page hides local demo credentials on Vercel.

Do not commit `.env` files, database files, or real passwords. `.env.example` contains placeholders only.

## Project layout

- `app.py` — Flask application, demo data, and database initialization/migration.
- `models/` — SQLAlchemy data models.
- `routes/` — authentication and role-specific pages.
- `templates/` — Jinja pages for each role.
- `public/static/` — CSS, JavaScript, cursors, and dashboard artwork.
- `database/schema.sql` — reference schema.
