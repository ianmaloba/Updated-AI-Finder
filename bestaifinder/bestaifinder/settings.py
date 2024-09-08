"""
Django settings for bestaifinder project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-o9*i%mj(&)_^urj0g8@zu@9i!m31^m1q@!#7ngybfzucxmcu1u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['24.144.124.10', 'localhost', '127.0.0.1:8000']
ALLOWED_HOSTS = ['*']


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
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.reddit',
    'easy_thumbnails',
    'filer',
    'mptt',
    'ckeditor_filebrowser_filer',
    'crispy_bootstrap4',
    'crispy_forms',
    'ckeditor',
    'ckeditor_uploader',
    'main',
    'userauth'
]

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'bestaifinder.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'userauth', 'templates'),
            os.path.join(BASE_DIR, 'main', 'templates'),
            os.path.join(BASE_DIR, 'templates'),
            ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'bestaifinder.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


# DATABASES ={
#   'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}

"""
# Digital Ocean
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ai-finder-guru',
        'USER': 'postgres',
        'PASSWORD': '@scientisT.1',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railway',
        'USER': 'postgres',
        'PASSWORD': 'NGbvcbNiJNlXifrTcxGliQeuYNEtjYhB',
        'HOST': 'meticulous-empathy.railway.internal',
        'PORT':'5432,
    }
}

"""

# Localhost
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ai-finder-guru',
        'USER': 'postgres',
        'PASSWORD': '@scientisT.1',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CRISPY_TEMPLATE_PACK = 'bootstrap4'


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


#CKEDITOR_CONFIGS = {
#    'default': {
#        'toolbar': 'full',
#        'height': 500,
#        'width': 700,
#   },
#}
"""
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ],
        'height': 300,
        'width': '100%',
    },
}
"""
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar': 'Full',
        'height': 300,
        'width': '100%',
        'toolbar_Full': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Flash', 'Table', 'HorizontalRule'],
            ['TextColor', 'BGColor'],
            ['Smiley', 'SpecialChar'],
            ['Source'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['NumberedList', 'BulletedList'],
            ['Indent', 'Outdent'],
            ['Maximize'],
            ['Scayt'],
            ['Blockquote', 'CodeSnippet'],
            ['Font', 'FontSize'],
            ['Find', 'Replace'],
            ['RemoveFormat', 'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord'],
            ['Subscript', 'Superscript'],
            ['Youtube', 'Iframe'],
            ['SelectAll', 'Print'],
        ],
        'extraPlugins': ','.join([
            'uploadimage',
            'div',
            'blockquote',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath',
            'codesnippet',
            'youtube',
            'iframe',
            'uploadfile',
        ]),
        'uploadUrl': '/ckeditor/upload/',
        'filebrowserBrowseUrl': '/ckeditor/browse/',
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserImageBrowseUrl': '/ckeditor/browse/',
        'filebrowserImageUploadUrl': '/ckeditor/upload/',
        'removeDialogTabs': 'image:advanced;link:advanced',
        'tabSpaces': 4,
        'allowedContent': True,
        'extraAllowedContent': 'iframe[*]',
        'contentsCss': ['/static/css/ckeditor_content.css'],
        'language': 'en',
        'entities': False,
        'entities_latin': False,
        'forcePasteAsPlainText': False,
        'removeFormatAttributes': '',
        'youtube_responsive': True,
        'youtube_related': False,
        'youtube_privacy': True,
        'youtube_width': '640',
        'youtube_height': '480',
        'enterMode': 2,
        'shiftEnterMode': 1,
    }
}
CKEDITOR_RESTRICT_BY_DATE = False


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# Media files (user-uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files (CSS, JavaScript, images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'bestaifinder/static'),
]

CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
if not DEBUG:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'bestaifinder', 'media')
    STATIC_ROOT = os.path.join(BASE_DIR, 'bestaifinder', 'static')
   
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',

    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    },
    
    'facebook': {
        'METHOD': 'oauth2',  # Set to 'js_sdk' to use the Facebook connect SDK
        #'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'EXCHANGE_TOKEN': True,
        #'LOCALE_FUNC': 'path.to.callable',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v13.0',
        'GRAPH_API_URL': 'https://graph.facebook.com/v13.0',
    },
    'github': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    },
    'reddit': {
        'AUTH_PARAMS': {'duration': 'permanent'},  # Make the Reddit OAuth token permanent
        'SCOPE': ['identity', 'submit'],  # Specify Reddit OAuth scopes
        'USER_AGENT': 'django:myappid:1.0 (by /u/AmbitiousDev-001)',  # Comply with Reddit API rules
    },
}

# Reddit API credentials
SOCIAL_AUTH_REDDIT_KEY = 'NWn2a6yePxSiv1FXkVTSHw'
SOCIAL_AUTH_REDDIT_SECRET = 'u54VNFomgGF0HhhcOn8W9DIceq6qcg'

LOGIN_REDIRECT_URL = '/'

#EMAIL
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER ='aifinderguru@gmail.com'
# EMAIL_HOST_PASSWORD ='@scientisT.2'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'aifinderguru@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'kfcf yiro ndmm duik')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'aifinderguru@gmail.com')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'aifinderguru@gmail.com')
APP_NAME = 'AI FINDER GURU'

