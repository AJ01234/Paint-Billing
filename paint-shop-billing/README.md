# Paint Shop Billing

Local-first billing software for paint shops built with FastAPI, SQLModel, SQLite, Jinja templates, and light JavaScript.

## Features in v1

- GST and non-GST billing
- Product inventory with brand, size, shade, HSN, GST, and stock
- Smart product search
- Painter/customer ledger
- Bill history and printable invoice page
- Low stock alerts
- Daily sales dashboard

## Run locally

```powershell
cd D:\paint-shop-billing
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://127.0.0.1:8000` on the shop computer, or `http://<shop-computer-ip>:8000` from a phone on the same Wi-Fi.

## V2 Hosting Prep

This project is now ready to move off the local computer:

- `DATABASE_URL` can point to PostgreSQL in production
- `Dockerfile` is included for container deploys
- `render.yaml` is included as a starter for Render
- `railway.json` is included as a starter for Railway
- `GET /healthz` is included for uptime checks
- `manifest.webmanifest` is included so the hosted app can be added to a phone home screen more cleanly

For hosted v2, set:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME
```

## Recommended V2 Path

1. Push this folder to GitHub.
2. Deploy the app to Render or Railway.
3. Attach a managed PostgreSQL database.
4. Set a custom domain such as `billing.anklikarpaints.in`.
5. Open that hosted URL on Android Chrome and tap `Add to Home screen`.

Then the same live data will appear on both phone and laptop.

## Notes

- Printing uses the browser print dialog from the invoice view.
- The database file is created locally as `paint_shop.db`.
- Seed data is inserted automatically the first time the app starts.
