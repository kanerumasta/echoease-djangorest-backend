
from pathlib import Path
from os import getenv, path
import dotenv
from django.core.management.utils import get_random_secret_key
from datetime import timedelta


#Cloudinary imports
# import cloudinary
# import cloudinary.api
# import cloudinary.uploader

APPEND_SLASH = True

BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_file = BASE_DIR / '.env.local'
TIME_ZONE = 'Asia/Manila'
USE_TZ = True

if path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)


SECRET_KEY = getenv('DJANGO_SECRET_KEY', get_random_secret_key())

DEBUG = getenv('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS = getenv('DJANGO_ALLOWED_HOSTS','127.0.0.1,8e6d-143-44-165-29.ngrok-free.app,192.168.1.242').split(',')

ALLOWED_HOSTS = ["*"]


# Application definition
INSTALLED_APPS = [
    'daphne',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',

    # 'cloudinary',
    'corsheaders',
    'rest_framework',
    'djoser',
    'social_django',
    'users',
    'artists',
    'chat',
    'booking',
    'payment',
    'dispute',
    'notification',
    'schedule',
    'transaction',
    'review',
    'logs',
    'custom_admin',
    #  'background_task',



]

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

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'


#edit
DATABASES = {
    'default':{
        "ENGINE":"django.db.backends.postgresql_psycopg2",
        "NAME":'echoeasev3',
        'USER':'postgres',
        'PASSWORD':'011456',
        'HOST':'127.0.0.1',
        'PORT':'5432'
    }
}



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True




STATIC_URL = '/static/'

MEDIA_URL = f'media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_DIRS = [
    BASE_DIR / "static",  # Add this if your static folder is at the project level
]

STATIC_ROOT = BASE_DIR / "staticfiles"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=20),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),

}

AUTHENTICATION_BACKENDS=[
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.CustomJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,

}

DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL' : 'password-reset/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL':True,
    'RESEND_ACTIVATION_EMAIL':True,
    'ACTIVATION_URL' : 'activation/{uid}/{token}',
    'USER_CREATE_PASSWORD_RETYPE':True,
    'PASSWORD_RESET_CONFIRM_RETYPE' : True,
    'TOKEN_MODEL' : None,
    'SOCIAL_AUTH_ALLOWED_REDIRECT_URIS' : getenv('REDIRECT_URLS').split(',') # type: ignore
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'users.UserAccount'

AUTH_COOKIE = 'access'
AUTH_COOKIE_ACCESS_MAX_AGE = 60 * 60
AUTH_COOKIE_REFRESH_MAX_AGE = 60 * 60 *24
AUTH_COOKIE_SECURE = getenv('AUTH_COOKIE_SECURE', 'True') == ' True'
AUTH_COOKIE_HTTP_ONLY = True
AUTH_COOKIE_PATH = '/'
AUTH_COOKIE_SAMESITE = 'strict'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = getenv('GOOGLE_AUTH_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = getenv('GOOGLE_AUTH_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = ['first_name','last_name']

SOCIAL_AUTH_FACEBOOK_KEY = getenv('FACEBOOK_AUTH_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = getenv('FACEBOOK_AUTH_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'email, first_name, last_name'
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = getenv('DEFAULT_FROM_EMAIL')
EMAIL_HOST_PASSWORD = getenv('EMAIL_HOST_PASSWORD')

SITE_NAME = 'Echoease'
DOMAIN = getenv('DOMAIN')

DISTANCE_MATRIX_API_URL = getenv('DISTANCE_MATRIX_API_URL')
DISTANCE_MATRIX_API_KEY = getenv('DISTANCE_MATRIX_API_KEY')


DEFAULT_FROM_EMAIL = getenv('DEFAULT_FROM_EMAIL')

#Django - Cloudinary Configuration
# cloudinary.config (

#     cloud_name = getenv('CLOUDINARY_CLOUD_NAME'),
#     api_secret = getenv('CLOUDINARY_SECRET'),
#     api_key = getenv('CLOUDINARY_KEY')

# )


# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("127.0.0.1", 6379)],
#         },
#     },
# }

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_BEAT_SCHEDULE = {

    'send_payment_reminder':{
        'task':'booking.tasks.send_payment_reminders',
        'schedule':60.0
    },
    'expire_bookings':{
        'task':'booking.tasks.expire_bookings',
        'schedule':60.0
    }
}

JAZZMIN_SETTINGS = {
    'site_title':'Echoease Admin',
    'site_header':'Echoease ',
    'site_brand':'Echoease Admin',

}

PAYMONGO_SECRET_KEY = getenv('PAYMONGO_SECRET_KEY')
XENDIT_BASE_URL = "https://api.xendit.co"

ENCRYPTION_KEY = getenv('ENCRYPTION_KEY')
XENDIT_SECRET_KEY = 'xnd_development_BsLQOooqeYdmo65EObu2e2q6RDdzmEW9o5agFJiRIpHL6Mq9dJ2oKy6nFI2Ht'

FACEBOOK_CLIENT_ID = getenv('FACEBOOK_CLIENT_ID')
FACEBOOK_CLIENT_SECRET = getenv('FACEBOOK_CLIENT_SECRET')
