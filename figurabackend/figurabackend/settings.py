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
SECRET_KEY = 'cr+2488qp=f^jb8r13j@wwsq2mxyqmh#zi_y603=-)zjahxvd2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
CORS_ORIGIN_ALLOW_ALL = True

ALLOWED_HOSTS = ['192.168.1.132', '127.0.0.1']

HASHID_FIELD_SALT = "#jnz3ol^8a@bfb)05*&zspnc-+$+_qqi^03+sjz1s7ql8z*lm^"

EMAIL_BACKEND = 'django_filebased_email_backend_ng.backend.EmailBackend'
EMAIL_FILE_PATH = '/mnt/c/Users/EIREXE/figuritas/tmpmail' # change this to a proper location

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MEDIA_ROOT='/mnt/c/Users/EIREXE/figuritas/backend/media'