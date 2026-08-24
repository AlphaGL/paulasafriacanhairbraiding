"""
Django settings for paulas_african project.
"""

from pathlib import Path

import dj_database_url
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent


# --- Core / security -------------------------------------------------------

SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-dev-only-key-change-me-before-real-use",
)

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost,.vercel.app,paulasafricanhairbraiding.store,www.paulasafricanhairbraiding.store",
    cast=Csv(),
)

# Needed for POST requests (booking form, studio login) to work once this is
# deployed behind Vercel's domain — Django checks the request's Origin header
# against this list for any cross-origin-looking POST.
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://*.vercel.app,https://paulasafricanhairbraiding.store,https://www.paulasafricanhairbraiding.store",
    cast=Csv(),
)

# Vercel terminates HTTPS at its edge and forwards to the app over plain HTTP,
# marking the original protocol in this header — without it, Django thinks
# every request is insecure even when the visitor is on https://.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# --- Applications ------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary_storage",
    "cloudinary",
    "core",
    "styles",
    "bookings",
    "studio",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "paulas_african.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "bookings.context_processors.business_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "paulas_african.wsgi.application"


# --- Database ----------------------------------------------------------------
# Uses a hosted Postgres (Neon) via DATABASE_URL when set. Falls back to local
# SQLite so the app can be built/tested before real credentials are plugged in.

DATABASE_URL = config("DATABASE_URL", default="")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# --- Password validation ------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- Internationalization ------------------------------------------------------

LANGUAGE_CODE = "en-us"

# Louisville, KY is in the US Eastern time zone.
TIME_ZONE = "America/New_York"

USE_I18N = True
USE_TZ = True


# --- Static & media files -------------------------------------------------------

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise serves static files directly from STATICFILES_DIRS at request time
# (rather than requiring a `collectstatic` build step first) — simplest option
# for a serverless deploy target like Vercel that has no persistent build step.
WHITENOISE_USE_FINDERS = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Cloudinary (image storage for hairstyle photos) ---------------------------

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME", default=""),
    "API_KEY": config("CLOUDINARY_API_KEY", default=""),
    "API_SECRET": config("CLOUDINARY_API_SECRET", default=""),
}
# CLOUDINARY_URL env var (if set) is picked up automatically by the cloudinary SDK too.

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Uses Cloudinary for image storage when real credentials are configured.
# Falls back to local disk storage otherwise, so image uploads work locally
# before Cloudinary is connected (mirrors the DATABASE_URL fallback above).
# Django 5.2 dropped the old DEFAULT_FILE_STORAGE setting in favor of STORAGES.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
if CLOUDINARY_STORAGE["CLOUD_NAME"]:
    STORAGES["default"]["BACKEND"] = "cloudinary_storage.storage.MediaCloudinaryStorage"


# --- Email -----------------------------------------------------------------
# Defaults to printing emails to the console for local development.
# Set EMAIL_BACKEND (and SMTP settings) in .env for real sending.

EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# Resend (HTTP API) is used instead of SMTP whenever a key is configured —
# more reliable than a blocking SMTP socket inside a serverless function
# (see bookings/email_backends.py). Falls back to SMTP/console otherwise.
RESEND_API_KEY = config("RESEND_API_KEY", default="")

if RESEND_API_KEY:
    EMAIL_BACKEND = "bookings.email_backends.ResendEmailBackend"
    # Resend's sandbox sender works with no domain setup, but can only deliver
    # to the email address on the Resend account itself — fine for now since
    # that's Paula's own inbox; once a real domain is verified with Resend,
    # set RESEND_FROM_EMAIL to an address on that domain to email customers too.
    DEFAULT_FROM_EMAIL = config("RESEND_FROM_EMAIL", default="onboarding@resend.dev")
else:
    EMAIL_BACKEND = config(
        "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
    )
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="Pauletteagbeti@gmail.com")

# Where new booking-request notifications are sent.
BUSINESS_NOTIFICATION_EMAIL = config(
    "BUSINESS_NOTIFICATION_EMAIL", default="Pauletteagbeti@gmail.com"
)


# --- Auth redirects (studio admin login) -----------------------------------

LOGIN_URL = "studio:login"
LOGIN_REDIRECT_URL = "studio:dashboard"
LOGOUT_REDIRECT_URL = "studio:login"
