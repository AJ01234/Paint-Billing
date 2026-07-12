# V2 Deployment Guide

This app can run independently on phone and laptop with the same live data, as long as it is deployed to a hosted backend and uses a shared production database.

## What v2 should be

- Hosted FastAPI web app
- Shared PostgreSQL database
- Custom domain like `billing.anklikarpaints.in`
- Same app works on phone and laptop
- Bills created on phone appear on laptop immediately, and vice versa

## Recommended stack

- App hosting: Render or Railway
- Database: Managed PostgreSQL
- Domain: Namecheap, GoDaddy, Cloudflare, or any registrar
- SSL: Provided automatically by the host
- Phone shortcut install: Web app manifest included in `app/static/manifest.webmanifest`

## Why not Netlify

Netlify is mainly for static frontends. This project has a Python backend and database, so it should be deployed on a platform that supports FastAPI directly.

Good link styles:

- `https://billing.anklikarpaints.in`
- `https://app.anklikarpaints.in`

Avoid relying on a default platform URL long-term if this is for real shop use.

## Render path

1. Push this project to GitHub.
2. Create a new Render Web Service from the repo.
3. Create a Render Postgres database.
4. Set `DATABASE_URL` from the database connection string.
5. Deploy using the included `render.yaml` or manual service setup.
6. Add your custom domain in Render settings.

## Railway path

1. Push this project to GitHub.
2. Create a new Railway project from the repo.
3. Add a PostgreSQL service in Railway.
4. Railway usually injects `DATABASE_URL` automatically; confirm it is present.
5. Deploy using the included `railway.json`.
6. Add your custom domain in Railway settings.

## Environment variables

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false
APP_BASE_URL=https://billing.yourdomain.in
APP_ENABLE_SCHEDULER=true
APP_SCHEDULER_POLL_SECONDS=60
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_PHONE=...
```

## Phone usage

Once hosted, your father only needs the web link.

On Android Chrome:

1. Open the app URL.
2. Tap the three-dot menu.
3. Tap `Add to Home screen`.

Then it behaves almost like an app shortcut.

## Important current limitation

This repo is now prepared for hosting, but it is not deployed yet. Actual phone-independent use starts only after:

1. the code is pushed to GitHub
2. the host service is created
3. PostgreSQL is attached
4. the production URL is live

## Smart billing automation now supported

- WhatsApp share links for invoice PDFs and daily report PDFs
- SMS sending through Twilio when credentials are configured
- daily owner report dispatch scheduler when `APP_ENABLE_SCHEDULER=true`

If Twilio credentials are not set, the app still queues outgoing notifications internally so you can review them in the dashboard and reports screens.

## Next v2 tasks

- Add authentication and shop owner login
- Add product import from Excel
- Add proper edit history / audit logging
- Add automated backups
- Add PWA manifest for better mobile install experience
