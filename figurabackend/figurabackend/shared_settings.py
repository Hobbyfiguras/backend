import os
import datetime
import corsheaders # for pireqs
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import psycopg2
except ImportError:
    # Fall back to psycopg2cffi
    from psycopg2cffi import compat
    compat.register()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'FigureSite',
    'django_resized',
    'ordered_model',
    'dry_rest_permissions',
    'channels',
    'haystack',
    'guardian'
]

ACCOUNT_ADAPTER ='FigureSite.adapters.FigureSiteAccountAdapter'

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Application definition

SITE_ID = 1

REST_USE_JWT = True

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
      'rest_framework_simplejwt.authentication.JWTAuthentication',
      'rest_framework.authentication.SessionAuthentication',
      'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
      'FigureSite.permissions.BaseObjectPermissions',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'threads': '5/h',
        'posts': '10/min',
    },
    'SERIALIZER_EXTENSIONS': {
        'AUTO_OPTIMIZE': True,
        'HASH_IDS_SOURCE': 'FigureSite.HASH_IDS',
        'USE_HASH_IDS': True
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=30)
}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'figurabackend.urls'

ACCOUNT_USERNAME_VALIDATORS = 'FigureSite.validators.validators'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR, 'templates', 'allauth')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = False
WSGI_APPLICATION = 'figurabackend.wsgi.application'
REST_SESSION_LOGIN = False

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'JPEG': ".jpg"}
GUARDIAN_MONKEY_PATCH = False
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

AUTH_USER_MODEL = 'FigureSite.User'

ASGI_APPLICATION = 'figurabackend.routing.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}