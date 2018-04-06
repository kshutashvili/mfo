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

TWILIO_ACCOUNT_SID = 'ACf55d9d99a44962e78c13798ccbeb9522'
TWILIO_AUTH_TOKEN = 'b273f33bdd09287ca70db6a6226ca0e3'
AUTHY_API_KEY = 'xVr6iPtwsTspiQU0LpJHWoyfcjoinqt6'

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
    #own
    'communication',
    'department',
    'content',
    'vacancy',
    'credit',
    'bids',
    'users',
    'token_confirm',
    'payment_gateways',
    #3-rd
    'ckeditor',
    'solo',
    'django_google_maps',
    'modeltranslation',
    'django_twilio',
    'rosetta'
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'efin',
        'USER': 'efin',
        'PASSWORD': 'efin',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


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

try:
    from .local_settings import *
except ImportError:
    pass
