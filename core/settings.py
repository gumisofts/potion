import os
from datetime import timedelta
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

load_dotenv(".env", override=True)
load_dotenv(".production.env", override=True)


env = os.getenv
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env("SECRET_KEY", get_random_secret_key())
DEBUG = env("DEBUG", False) == "True"

ALLOWED_HOSTS = env("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")


CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
CORS_ALLOW_CREDENTIALS = True

AUTH_USER_MODEL = "accounts.User"
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_celery_beat",
    "enterprises",
    "bills",
    "notifications",
    "files",
    "accounts",
    "wallets",
    "subscriptions",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["notifications/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.app"
ASGI_APPLICATION = "core.asgi.app"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("PG_DB_NAME"),
        "USER": env("PG_USER"),
        "PASSWORD": env("PG_PASSWORD"),
        "HOST": env("PG_HOST"),
        "PORT": env("PG_PORT", "5432"),
        "CONN_MAX_AGE": None,
        "OPTIONS": {"sslmode": env("PG_SSL_MODE")},
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = env("STATIC_URL", "static/")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "enterprises.authentications.EnterpriseAPIKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

EMAIL_USE_SSL = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USER = env("EMAIL_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_USER_PASSWORD")

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", "eu-north-1")

ADMIN = ("Murad", "nuradhussen082@gmail.com")

CELERY_BROKER_URL = f"redis://{env('REDIS_USERNAME','default')}:{env('REDIS_PASSWORD','')}@{env('REDIS_HOST','localhost')}:{env('REDIS_PORT',6379)}"
CELERY_BACKEND_URL = f"redis://{env('REDIS_USERNAME','default')}:{env('REDIS_PASSWORD','')}@{env('REDIS_HOST','localhost')}:{env('REDIS_PORT',6379)}"

AUTHENTICATION_BACKENDS = [
    "accounts.backends.PhoneAuthenticationBackend",
]


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=90),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
}


SPECTACULAR_SETTINGS = {
    "TITLE": "API Documentation",
    "DESCRIPTION": "Description of documentation",
    "VERSION": "0.0.1",
    "SERVE_INCLUDE_SCHEMA": True,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "SERVERS": [
        {
            "url": "https://potion.dev.gumisofts.com",
            "description": "Active Development Server",
        },
        {
            "url": "https://potion.v01.gumisofts.com",
            "description": "V01 Production Server",
        },
        {
            "url": "http://localhost:8000",
            "description": "Local Development Server",
        },
    ],
}


CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
GOOGLE_APPLICATION_CREDENTIALS = {
    "type": "service_account",
    "project_id": env("GOOGLE_APPLICATION_CREDENTIALS_PROJECT_ID"),
    "private_key_id": env("GOOGLE_APPLICATION_CREDENTIALS_PRIVATE_KEY_ID"),
    "private_key": "-----BEGIN PRIVATE KEY-----\n"
    + "\n".join(env("GOOGLE_APPLICATION_CREDENTIALS_PRIVATE_KEY", "").split("\\n"))
    + "\n-----END PRIVATE KEY-----\n",
    "client_email": env("GOOGLE_APPLICATION_CLIENT_EMAIL"),
    "client_id": env("GOOGLE_APPLICATION_CREDENTIALS_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": env("GOOGLE_APPLICATION_CREDENTIALS_CERT_URL"),
    "universe_domain": "googleapis.com",
}
