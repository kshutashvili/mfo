"""
Django settings for efin project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-w8(up#n)ea%v0@5olsz37y(kt8!^@p(750bqp4#=hs-%n7n7y'
GOOGLE_MAPS_API_KEY = 'AIzaSyAntT27HQnaY0z2nOKEk7eyEimuzZOerMM'

TWILIO_ACCOUNT_SID = 'ACbe26b6146caf3657c7133a88dc0873e4'
TWILIO_AUTH_TOKEN = 'e2d909069a7d4c5bd0f9e2064a3bbf43'
TWILIO_PHONE_NUMBER = '+18507357830'
AUTHY_API_KEY = 'nN5b8SSVsNBz34Vj9BfMVUu7Mxg69Mrf'
# 'xVr6iPtwsTspiQU0LpJHWoyfcjoinqt6'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # own
    'communication',
    'department',
    'content',
    'vacancy',
    'credit',
    'bids',
    'users',
    'token_confirm',
    'payment_gateways',
    'payments',
    'bankid',
    # 3-rd
    'ckeditor',
    'solo',
    'django_google_maps',
    'modeltranslation',
    'django_twilio',
    'rosetta',
    'raven.contrib.django.raven_compat',
    'rangefilter',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'efin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'content.context_processors.menu_processor',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'efin.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'efin',
#         'USER': 'efin',
#         'PASSWORD': 'efin',
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'efin_new',
        'USER': 'efin',
        'PASSWORD': 'efin',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

TURNES_HOST = "10.10.100.27"
TURNES_USER = "root"
TURNES_PASSWORD = "Orraveza(99)"
TURNES_DATABASE = "mbank"

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'users.User'

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_L10N = True

USE_TZ = True

gettext = lambda s: s
LANGUAGES = (
    ('ru', gettext('Russian')),
    ('ua', gettext('Ukrainian')),
)

MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Email от заказчиков
EMAIL_HOST_USER = 'robot@expressfinance.com.ua'
EMAIL_HOST_PASSWORD = 'Qwerty+1'
EMAIL_HOST = 'mail.expressfinance.com.ua'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ADMIN_EMAIL = 'robot@expressfinance.com.ua'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')
PROTECTED_MEDIA_URL = '/protected/'
PROTECTED_MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'protected')
PROTECTED_MEDIA_LOCATION_PREFIX = '/internal'
PROTECTED_MEDIA_SERVER = 'nginx'
PROTECTED_MEDIA_AS_DOWNLOADS = False

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'profile'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

GEOIP_PATH = BASE_DIR + '/geoip'

PB_SERVICE_CODE = 1
EASYPAY_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'


# 4bill settings
PROVIDER_4BILL_ACCOUNT = 103
PROVIDER_4BILL_WALLET = 184
PROVIDER_4BILL_POINT = 94
PROVIDER_4BILL_SERVICE = 2
PROVIDER_4BILL_API_KEY = 'ytb23Bda8fhUX@omw7'


# Privat payment URL for LK
PRIVAT_PAYMENT_URL = "https://my-payments.privatbank.ua/mypayments/customauth/identification/fp/static?staticToken=bfcacc2bad3ece1037cc9262f866ce5exb5favsl&acc="


# BankID credentials
BANKID_CLIENT_ID = 'b0f1d8f4-9775-49b4-b82f-807fbacc385a'
BANKID_SECRET = 'N2Y2ZGQ0YjgtYTAyNC00MTkyLTgyZDMtZDNhZjMxM2E5MjQw'

RAVEN_CONFIG = {
    'dsn': 'https://37c01da58b9341bf88fa4b234044539f:1e3f3fa719e043058763110f38433784@sentry.io/1227127',
}

# telegram
# test group
TEST_API_KEY = '580592832:AAFV-gWcD4HL6F-FljmrASDyK-O-9hcHgLc'
TEST_GROUP_ID = '-266220155'

try:
    from efin.local_settings import *
except ImportError:
    pass
