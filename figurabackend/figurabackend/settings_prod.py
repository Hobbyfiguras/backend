"""
Django settings for figurabackend project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import datetime
from .shared_settings import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
with open('/etc/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']


# SECURITY WARNING: keep the secret key used in production secret!
with open('/etc/hashid_secret.txt') as f:
    HASHID_FIELD_SALT = f.read().strip()

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'figuresite',
        'USER': 'figuresite',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

MEDIA_ROOT='/server/live/media'
STATIC_ROOT='/server/live/static'