from pathlib import Path
import environ
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# 3 parents up: base.py -> settings/ -> config/ -> root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize environ
env = environ.Env()
# Read the .env file (Only for local! On EC2, we'll pass variables differently or point to a specific file)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')

# --- django-allauth Settings ---
SITE_ID = 1

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.postgres',
    
    # 3rd Party
    'allauth',
    'allauth.account',
    
    # Local Apps
    'apps.core',
    'apps.accounts',
    'apps.titles',
    'apps.people',
    'apps.interactions',
    'apps.social',
    'apps.lists',
    'apps.search',
]

MIDDLEWARE = [
    'apps.accounts.middleware.ProxyIPMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}

# Authentication Settings
AUTH_USER_MODEL = 'accounts.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Password validation, Internationalization, Static, Default primary key...
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Where to send users after they log in or log out
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# --- NEW PROXY FIXES ADDED HERE ---
# 1. Tell allauth we are strictly on HTTP right now, so it stops checking for secure HTTPS referers
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

# 2. Disable allauth's aggressive rate-limiting so your IP gets unbanned
ACCOUNT_RATE_LIMITS = {}

# ==========================================
# EMAIL & ALLAUTH CONFIGURATION (PRODUCTION READY)
# ==========================================

# 1. Use actual SMTP servers instead of the terminal
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# 2. Your Gmail Credentials
EMAIL_HOST_USER = 'hey.cineverse@gmail.com' # Put your Gmail here
EMAIL_HOST_PASSWORD = 'fydllwzmpksysnsf'     # Put your 16-character App Password here (spaces don't matter)

# 3. What the user sees in their inbox
DEFAULT_FROM_EMAIL = 'CineVerse <hey.cineverse@gmail.com>'

# 2. Tell Allauth to care about emails
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[CineVerse]"

# 3. Security configurations
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300