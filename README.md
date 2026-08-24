# Paula's African Hair Braiding — Website

A Django website for booking hair braiding appointments. Customers browse hairstyles by
category, see pricing (including a travel fee if Paula comes to them), and submit a booking
request. Paula manages everything — styles, photos, prices, and bookings — from a custom
admin dashboard at `/studio/`.

## Tech stack

- **Backend:** Django (Python)
- **Database:** Neon (hosted Postgres) — falls back to local SQLite automatically if no
  `DATABASE_URL` is set, so you can run the app immediately
- **Images:** Cloudinary
- **Frontend:** Django templates + vanilla HTML/CSS/JS (no frontend framework)
- **Email:** Resend (HTTP API — booking requests are emailed, not paid online). Falls back to
  SMTP/console if no Resend key is set.
- **Deployment:** Vercel (see section 6)

## Project layout

- `core/` — home, about/contact pages
- `styles/` — hairstyle categories, styles (with prices/photos), public browse & detail pages
- `bookings/` — the booking form, booking model, business settings, email sending
- `studio/` — the custom admin dashboard (login-protected, at `/studio/`)
- `templates/`, `static/` — all HTML/CSS/JS
- `api/index.py`, `vercel.json` — Vercel deployment entrypoint/config

## Current status

`.env` is already filled in with real credentials:

- **Database:** Neon Postgres (real, not SQLite) — already migrated and seeded.
- **Images:** Cloudinary (`zydojvwr`) — already storing the 10 starter styles' photos.
- **Studio login:** username `paulette`, password `HpyD97qjyM15u7` — **change this**, see
  section 5. This is a real production credential now, not a local-only placeholder.
- **Email:** still the console backend (prints to terminal) — no Resend API key has been
  provided yet, see section 4.

## 1. Run it locally

```bash
# from the project folder
venv\Scripts\activate          # Windows
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the public site and `http://127.0.0.1:8000/studio/` for the
admin dashboard. Because `.env` already points at the real Neon database and Cloudinary, this
is editing the same data that will show up live once deployed — there's no separate "demo"
database anymore.

## 2. Database (Neon)

Already connected. If you ever need to point at a different Postgres database (Neon, Supabase,
anything), just change `DATABASE_URL` in `.env` — any standard Postgres connection string
works — then run:

```bash
python manage.py migrate
python manage.py seed_initial_data
python manage.py createsuperuser
```

If `DATABASE_URL` is ever removed from `.env`, the app automatically falls back to local
SQLite instead of erroring out.

## 3. Cloudinary (photo uploads)

Already connected. Photo uploads from Studio go straight to Cloudinary now. If Cloudinary
credentials are ever removed from `.env`, uploads automatically fall back to local disk
storage under `media/` instead of erroring out.

## 4. Email sending (Resend) — already connected

**Status: live.** `RESEND_API_KEY` is set, and the domain `noreply.paulasafricanhairbraiding.store`
is verified with Resend, so both booking emails deliver to any address now — not just to the
Resend account owner. Sender is `RESEND_FROM_EMAIL` in `.env`
(`bookings@noreply.paulasafricanhairbraiding.store`).

Both emails are sent as HTML (styled, matching the site's branding — logo, colors, a details
table, a CTA button) with a plain-text fallback for email clients that don't render HTML.
Templates: `templates/bookings/email/*.html` (styled) and `*.txt` (plain-text fallback), built
from a shared `email_base.html` layout.

**Why Resend instead of Gmail SMTP:** this app runs on Vercel as a serverless function. SMTP
needs a blocking socket connection held open during the request — fine on a normal server, but
a real risk of occasional timeouts in a serverless function with a hard execution limit.
Resend sends over a plain HTTP request instead, which is faster and doesn't have that failure
mode. `bookings/email_backends.py` implements this; `bookings/emails.py` just builds the
message the same way it always did.

If `RESEND_API_KEY` is ever removed from `.env`, the app automatically falls back to SMTP (see
`EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` for a Gmail App Password setup) or the console backend
if that's blank too.

**Remember for Vercel:** add `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, and `SITE_URL` (used to
build the logo image URL and website links inside the emails) to Vercel's environment
variables too — local `.env` only affects your machine (section 6).

Every booking request sends two emails: one to `BUSINESS_NOTIFICATION_EMAIL` (Paula, with full
customer/booking details and a reply-to set to the customer) and a confirmation to the
customer.

## 5. Change the admin password

```bash
python manage.py changepassword paulette
```

This updates whichever database `DATABASE_URL` currently points at — since that's the real
Neon database, running this locally changes the live production login too. No separate "deploy
the password change" step needed.

## 6. Deploying to Vercel

Django isn't Vercel's typical use case (it's built for serverless functions, not long-running
servers), but it works here through a small adapter already in place:

- `api/index.py` exposes the Django app as a Vercel Python serverless function.
- `vercel.json` routes every request to it.
- `whitenoise` serves static files (CSS/JS) directly from the function — no separate build
  step needed.
- Media (uploaded photos) already goes to Cloudinary, not local disk — required, since
  serverless functions don't persist files between requests.

Steps:

1. **Push this repo to GitHub** (see section 7 below if not done yet).
2. In the [Vercel dashboard](https://vercel.com/new), import the GitHub repo.
3. Under **Project Settings → Environment Variables**, add every value currently in `.env`:
   `SECRET_KEY`, `DEBUG` (set to `False`), `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `SITE_URL`,
   `DATABASE_URL`, `CLOUDINARY_URL`, `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`,
   `CLOUDINARY_API_SECRET`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL`,
   `BUSINESS_NOTIFICATION_EMAIL`.
   - Once the custom domain is connected (still a separate step — see below), update `SITE_URL`
     to `https://paulasafricanhairbraiding.store` so email logo/links point at the real domain
     instead of the `.vercel.app` one.
   - **Important:** set `DEBUG=False` in Vercel. Never deploy with `DEBUG=True` — it exposes
     stack traces and settings publicly to anyone who visits a broken URL.
4. Click Deploy. Vercel installs `requirements.txt` and runs `api/index.py` as the app.
5. Once deployed, your admin login is at `https://<your-project>.vercel.app/studio/`.

No local media/SQLite/test data gets deployed — production reads live from Neon and
Cloudinary, same as your local `.env` does right now.

## 7. Pushing to GitHub

`.env`, `venv/`, `db.sqlite3`, and `media/` are all git-ignored, so none of your real
credentials, the local dev database copy, or locally-cached photos will ever get committed —
only source code.

```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/AlphaGL/paulasafriacanhairbraiding.git
git push -u origin main
```

## How booking pricing works

Each style has one price (`salon_price`) for when the customer comes to Paula. If the customer
selects "Paula comes to me," the flat **travel fee** (set in Studio → Business Settings) is
added automatically. The price shown to the customer and stored on the booking is snapshotted
at booking time, so changing prices later doesn't rewrite past bookings.

## What's intentionally not included

- Online payment — bookings are requests only; Paula follows up by email.
- Distance-based travel pricing — the travel fee is one flat amount, editable in Studio.
- Customer accounts — booking is guest-only (name/email/phone per booking).
