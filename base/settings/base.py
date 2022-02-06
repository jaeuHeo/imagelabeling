"""
Django settings for Neo4j project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import json
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^zw*d-__n^e=32epn6d@(^uejs#zb8(^e8wy^g=try8!kc^liw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition
CORS_ALLOW_HEADERS = (
    'Accept',
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-csrftoken',
    'user-agent',
    'accept-encoding',
    'wehago-sign',
    'corsheaders',
    'service-code',
    'service-key',
    'client-id',
    'timestamp',
    'transaction-id',
    'h-portal-id',
    'H-Portal-Id',
    'cno',
    'lp_sign',
    'token',
    'cache-control',
    'cookie'
)

# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_CREDENTIALS = True
#
# CSRF_TRUSTED_ORIGINS = [
#         # 'http://10.106.2.55:8001/',
#     'http://local.wehago.com:3000/',
#     'http://10.106.6.61:3000/'
#
#     ]
#
# CORS_ALLOWED_ORIGINS = [
#     # 'http://10.106.2.55:8001/',
#     'http://local.wehago.com:3000/',
#     'http://10.106.6.61:3000/'
# ]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'middleware.kibana_rmfile.FileRemoveMiddleware',
    'middleware.kibana_log.LogAndExceptionController',
    'middleware.kibana_db.DatabaseErrorMiddleware',

]

MIDDLEWARE = MIDDLEWARE_CLASSES

ROOT_URLCONF = 'base.urls'



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
            ],
        },
    },
]



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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'


CACHE_MIDDLEWARE_SECONDS = 31449600


MAX_UPLOAD_SIZE = "5242880"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'ERROR',
            'filters': None,
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}


ROOT_PATH = '/'.join(BASE_DIR.split('/')[:-1])
# print(ROOT_PATH)
# MEDIA_PATH = os.path.join(ROOT_PATH, 'img/')
MEDIA_PATH = '/img_labeling/img/'
MEDIA_ROOT = MEDIA_PATH
MEDIA_URL = '/imglabeling/static/'
# SAVE_IMG_PATH = MEDIA_PATH

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, '../db_config/')

SERVICE_NAME = 'label'