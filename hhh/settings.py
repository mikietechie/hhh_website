from pathlib import Path
import sys
import os
import datetime

from dotenv import load_dotenv

load_dotenv()
env = os.environ

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.get("SECRET_KEY")

DEBUG = int(env.get("DEBUG", 1))
ALLOWED_HOSTS = env.get("ALLOWED_HOSTS", "").split(",")
# CORS_ALLOWED_ORIGINS =  env["CORS_ALLOWED_ORIGINS"].split(",")
# CORS_ALLOW_ALL_ORIGINS = True
SITE_URL = env.get("SITE_URL", "http://localhost:8000")
INTERNAL_IPS = ["127.0.0.1"]
TEST = 'test' in sys.argv[1:]
MAKEMIGRATIONS = 'makemigrations' in sys.argv[1:]
MIGRATE = 'migrate' in sys.argv[1:]
LOADING = 'loaddummydata' in sys.argv[1:]

CRISPY_TEMPLATE_PACK = "bootstrap4"

## APPS

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    # 'crispy_forms',
    # 'crispy_bootstrap4',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',
    # 'tinymce',
    'debug_toolbar',
]

MY_APPS = [
    "app",
    'website',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + MY_APPS

## MIDDLEWARE & URLS & TEMPLATES

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'hhh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # 'sapp.context.meta.meta_context',
                # 'sapp_abelpro.context.template_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'hhh.wsgi.application'

# MODELS
AUTH_USER_MODEL = "app.User"

# AUTH USER
LOGIN_URL = "/auth/login/"
LOGOUT_URL = "/auth/logout/"
RECOVER_URL = "/auth/recover/"
REGISTER_URL = "/auth/register/"

DATABASES = {
    'default': {
        'ENGINE': env.get("DATABASE_BACKEND") or "django.db.backends.sqlite3",
        'NAME': env.get('DATABASE_NAME') or BASE_DIR / 'db.sqlite3',
        'USER': env.get('DATABASE_USER'),
        'PASSWORD': env.get('DATABASE_PASSWORD'),
        'HOST': env.get('DATABASE_HOST'),
        'PORT': env.get('DATABASE_PORT')
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATICFILES_DIRS = []


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.joinpath("static")

MEDIA_ROOT = BASE_DIR.joinpath('media')
MEDIA_URL = '/media/'

## EMAIL

EMAIL_BACKEND = env.get("EMAIL_BACKEND")
EMAIL_HOST = env.get("EMAIL_HOST")
EMAIL_USE_TLS = env.get("EMAIL_USE_TLS") or None
EMAIL_USE_SSL = env.get("EMAIL_USE_SSL") or None
EMAIL_PORT = int(env.get("EMAIL_PORT"))
EMAIL_HOST_USER = env.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env.get("DEFAULT_FROM_EMAIL")

## FIELDS
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

## RESTFRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}


## JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=5),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': datetime.timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': datetime.timedelta(days=1),
}


## TinymCE
TINYMCE_DEFAULT_CONFIG = {
    "height": "160px",
    "width": "100%",
    "menubar": "file edit view insert format tools table help",
    "plugins": "advlist autolink lists link image charmap print preview anchor searchreplace visualblocks code "
    "fullscreen insertdatetime media table paste code help wordcount spellchecker",
    "toolbar": "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft "
    "aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor "
    "backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | "
    "fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | "
    "a11ycheck ltr rtl | showcomments addcomment code",
    "custom_undo_redo_levels": 10,
    # "language": "es_ES",  # To force a specific language instead of the Django current language.
}

# Stripe
STRIPE_SECRET_KEY = env.get("STRIPE_SECRET_KEY")
STRIPE_ENDPOINT_SECRET = env.get("STRIPE_ENDPOINT_SECRET")