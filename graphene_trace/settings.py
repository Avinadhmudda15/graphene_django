"""
Django settings for Graphene Trace – Sensore Platform
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-graphene-trace-dev-key-change-in-production-2024'
DEBUG = True
# Dev: allow any host header (localhost, 127.0.0.1, your LAN IP, custom names in hosts file)
ALLOWED_HOSTS = ['*']

# Shown in browser tab and sidebar (case study product name)
SITE_NAME = 'Sensore'
SITE_TITLE = 'Sensore — Graphene Trace'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'dashboard',
    'data_processing',
    'analytics',
    'reports',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'graphene_trace.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'graphene_trace.context_processors.site_branding',
            ],
        },
    },
]

WSGI_APPLICATION = 'graphene_trace.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 6}},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ── Sensor thresholds ──────────────────────────────────────
PRESSURE_ALERT_THRESHOLD = 500   # trigger alert above this
CONTACT_THRESHOLD        = 50    # pixel counts as "contact" above this
MIN_REGION_PIXELS        = 10    # min connected pixels for PPI
DATA_UPLOAD_MAX_MB       = 200

# Login/forms work when you open the app by these URLs (add LAN IP if you use phone on Wi‑Fi)
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://sensore.local:8000',
]
for _origin in os.environ.get('DJANGO_CSRF_EXTRA_ORIGINS', '').split(','):
    _origin = _origin.strip()
    if _origin:
        CSRF_TRUSTED_ORIGINS.append(_origin)
