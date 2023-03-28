import os
from os.path import abspath
from os.path import dirname
import secrets

from datetime import timedelta

from .utils import get_env, create_file


# main runtime system settings

CURRENT_DIR = dirname(abspath(__file__))
BASE_DIR = dirname(CURRENT_DIR)
ROOT_DIR = dirname(BASE_DIR)
DEBUG = get_env('DEBUG', False, True)
SITE_NAME = get_env('SITE_NAME', 'SITE NAME NOT SET')
ENVIRONMENT = get_env('ENVIRONMENT', 'production')
SECRET_KEY = get_env('SECRET_KEY', secrets.token_hex(30))
ALLOWED_HOSTS = get_env('ALLOWED_HOSTS', 'production').split()
GITHUB_WEBHOOK_SECRET = get_env('GITHUB_WEBHOOK_SECRET', "")
LOG_DIR = get_env('LOG_DIR', BASE_DIR + "/tmp/")


# security settings

# https://docs.djangoproject.com/en/4.0/ref/middleware/#http-strict-transport-security
SECURE_HSTS_SECONDS = int(get_env('SECURE_HSTS_SECONDS', 3600))

# https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-SECURE_SSL_REDIRECT
SECURE_SSL_REDIRECT = get_env('SECURE_SSL_REDIRECT', False, True)

# https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-SESSION_COOKIE_SECURE
SESSION_COOKIE_SECURE = get_env('SESSION_COOKIE_SECURE', False, True)

# https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-CSRF_COOKIE_SECURE
CSRF_COOKIE_SECURE = get_env('CSRF_COOKIE_SECURE', False, True)

# https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-SECURE_HSTS_INCLUDE_SUBDOMAINS
SECURE_HSTS_INCLUDE_SUBDOMAINS = get_env('SECURE_HSTS_INCLUDE_SUBDOMAINS', False, True)

# https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-SECURE_HSTS_PRELOAD
SECURE_HSTS_PRELOAD = get_env('SECURE_HSTS_PRELOAD', False, True)

# https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-SECURE_BROWSER_XSS_FILTER
SECURE_BROWSER_XSS_FILTER = get_env('SECURE_BROWSER_XSS_FILTER', False, True)

# https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-SECURE_PROXY_SSL_HEADER
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Setting the Referrer-Policy Header
# Django 3.x also added the ability to control the Referrer-Policy header. You can specify SECURE_REFERRER_POLICY in project/settings.py:
SECURE_REFERRER_POLICY = get_env('SECURE_REFERRER_POLICY', "strict-origin-when-cross-origin")


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Application apps

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # third apps
    'simple_history',
    'rest_framework',
    'corsheaders',
    'tinymce',
    'post_office',
    'django_cleanup.apps.CleanupConfig',
    'django_celery_results',
    'adminsortable2',
    'django_celery_beat',

    # application apps
    'apps.abstract.apps.AbstractConfig',
    'apps.config.apps.ConfigConfig',
    'apps.grievance.apps.GrievanceConfig',
    'apps.notification.apps.NotificationConfig',
    'apps.person.apps.PersonConfig',
    'apps.project.apps.ProjectConfig',
    'apps.utils.apps.UtilsConfig',

    # django health-check (third app)
    'health_check',                      # required
    'health_check.db',                   # stock Django health checkers
    'health_check.cache',                # application python cache
    'health_check.storage',              # armazenamento
    'health_check.contrib.migrations',   # migrações do banco de dados
    'health_check.contrib.celery',       # celery
    'health_check.contrib.celery_ping',  # celery
    'health_check.contrib.psutil',       # disk and memory utilization
    'health_check.contrib.rabbitmq',     # requires RabbitMQ broker
]


# Application middlewares

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # track and populate the user model chagens history automatically
    # https://django-simple-history.readthedocs.io/en/latest/quick_start.html#install
    'simple_history.middleware.HistoryRequestMiddleware',

    # Add custom middleware
    # 'config.middleware.HealthCheckMiddleware',

    # middleware for html minification
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware'
]


# Application urls

ROOT_URLCONF = 'application.urls'


# Para ativar o modal em vez de outra janela
# na configuração do tema (jazzmin) do admin
# https://docs.djangoproject.com/en/4.0/ref/clickjacking

X_FRAME_OPTIONS = 'SAMEORIGIN'
XS_SHARING_ALLOWED_METHODS = ['GET']


# They correspond to a filter that all intercept
# all of our application’s requests and apply CORS logic to them.
# However, since we’re working full localhost, we’ll disable the CORS
# feature by adding the following to the same file:

CORS_ORIGIN_ALLOW_ALL = True


# Django jinja template settings

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR + '/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# WSGI config

WSGI_APPLICATION = 'application.wsgi.application'


# Database config
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_env('DATABASE_NAME', ""),
        'USER': get_env('DATABASE_USER', ""),
        'PASSWORD': get_env('DATABASE_PASS', ""),
        'HOST': get_env('DATABASE_HOST', ""),
        'PORT': get_env('DATABASE_PORT', 3306),
        'CONN_MAX_AGE': 60,
        'TIME_ZONE': 'America/Sao_Paulo',
        'OPTIONS': {
            'ssl': ENVIRONMENT == 'production'
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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


# Email settings

EMAIL_BACKEND = get_env('EMAIL_BACKEND', "post_office.EmailBackend")
EMAIL_HOST = get_env('EMAIL_HOST', "")
EMAIL_PORT = get_env('EMAIL_PORT', "")
EMAIL_HOST_USER = get_env('EMAIL_HOST_USER', "")
EMAIL_HOST_PASSWORD = get_env('EMAIL_HOST_PASSWORD', "")
EMAIL_USE_TLS = get_env('EMAIL_USE_TLS', "", True)
EMAIL_USE_SSL = get_env('EMAIL_USE_SSL', "", True)
EMAIL_FILE_PATH = get_env('EMAIL_FILE_PATH', BASE_DIR + "/tmp")
DEFAULT_FROM_EMAIL = get_env('DEFAULT_FROM_EMAIL', "")
SERVER_EMAIL = DEFAULT_FROM_EMAIL


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'America/Sao_Paulo'
DATETIME_FORMAT = "d/m/Y H:s"
LANGUAGE_CODE = 'pt-BR'
LANGUAGES = [('pt', 'Português')]


# Url where redirect user after logout
# https://docs.djangoproject.com/en/4.1/ref/settings/#logout-redirect-url

LOGOUT_REDIRECT_URL = "/admin/login"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = get_env('STATIC_URL') + '/static/'
STATIC_HOST = get_env('STATIC_URL') if not DEBUG else ""
STATICFILES_DIRS = [
    # BASE_DIR + '/config/static/',
    # BASE_DIR + '/notification/static/',
]
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# The dynamic path used in production where django save attached files
# like images and docs.

DINAMYC_FILES_PATH = ROOT_DIR + '/gavos.uploads/'

# The path where django copy all assets and
# images after collectstatic command.

STATIC_ROOT = DINAMYC_FILES_PATH + 'static/'


# To handle file uploads from admin

MEDIA_URL = get_env('MEDIA_URL') + '/media/'
MEDIA_ROOT = DINAMYC_FILES_PATH + 'uploads/media/'
SEMINOVO_IMAGE_MINIMUM_WIDTH = 1024
SEMINOVO_IMAGE_MINIMUM_HEIGHT = 768


# API REST configurations
# https://www.django-rest-framework.org/tutorial/quickstart

REST_FRAMEWORK = {
    'PAGE_SIZE': 9,
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_METADATA_CLASS': None,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'django.contrib.auth',
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FileUploadParser',
        'rest_framework.parsers.FormParser',
    ),
}


# Settings for django-htmlmin
# https://github.com/cobrateam/django-htmlmin

HTML_MINIFY = ENVIRONMENT != 'development'


# Settings for django-tinymce - add TinyMCE
# editor into Django admin forms (TextArea)
# https://github.com/jazzband/django-tinymce

TINYMCE_DEFAULT_CONFIG = {
    "height": "450px",
    "width": "82%",
    "border-radius": "5px",
    "menubar": "file edit view insert format tools table help",
    "plugins": "advlist autolink lists link image charmap print preview anchor searchreplace visualblocks code "
    "fullscreen insertdatetime media table paste code help wordcount",
    "toolbar": "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft "
    "aligncenter alignright alignjustify | outdent indent | numlist bullist checklist | forecolor "
    "backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | "
    "fullscreen preview save print | insertfile image media pageembed template link anchor codesample | "
    "a11ycheck ltr rtl | showcomments addcomment code",
    "custom_undo_redo_levels": 30,
    "language": "pt_BR",
}


# Django JWT config
# https://django-rest-framework-simplejwt.readthedocs.io/en/latest

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=2),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS512',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=300),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=2),
}


# POST_OFFICE async email lib settings
# https://github.com/ui/django-post_office

POST_OFFICE = {
    # The SMTP standard requires that each email contains a unique Message-ID.
    'MESSAGE_ID_ENABLED': True,

    # Otherwise, if MESSAGE_ID_FQDN is unset (the default), django-post_office
    # falls back to the DNS name of the server, which is determined by the
    # network settings of the host.
    'MESSAGE_ID_FQDN': "gavos.com.br",

    # Log only failed deliveries.
    # The different options are:
    #   0 logs nothing
    #   1 logs only failed deliveries
    #   2 logs everything (both successful and failed delivery attempts)
    'LOG_LEVEL': 2,

    # Delivering emails through the Celery worker.
    'CELERY_ENABLED': True,

    # The default priority for emails is medium, but this can be altered here.
    # Integration with asynchronous email backends (e.g. based on Celery)
    # becomes trivial when set to now.
    'DEFAULT_PRIORITY': 'now',

    # Here we automatically requeue failed email deliveries (is not activated
    # by default).
    'MAX_RETRIES': 3,

    # Schedule to be retried 15 minutes later
    'RETRY_INTERVAL': timedelta(minutes=3),
}
POST_OFFICE_CACHE = False


# Django Admin Theme config
# https://django-jazzmin.readthedocs.io/configuration

JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if
    # absent or None)
    "site_title": SITE_NAME,

    # Title on the brand, and login screen (19 chars max) (defaults to
    # current_admin_site.site_header if absent or None)
    "site_header": SITE_NAME,

    # Title on the brand (19 chars max) (defaults to
    # current_admin_site.site_header if absent or None)
    "site_brand": SITE_NAME,

    # Logo to use for your site, must be present in static files, used for
    # brand on top left
    "site_logo": "/img/logo.png",

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img",

    # Relative path to a favicon for your site, will default to site_logo if
    # absent (ideally 32x32 px)
    "site_icon": "/img/logo.png",

    # Welcome text on the login screen
    "welcome_sign": "Bem vindo a " + SITE_NAME,

    # Copyright on the footer
    "copyright": get_env('COPYRIGHT_NAME'),

    # The model admin to search from the
    # search bar, search bar omitted if excluded
    "search_model": [],

    # Links to put along the top menu
    "topmenu_links": [
        # {"name": "Ajuda", "url": "/sobre-o-sistema", "permissions": ["auth.view_user"]},
    ],

    "use_google_fonts_cdn": True,

    # Field name on user model that contains avatar image
    "user_avatar": None,

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    "fixed_sidebar": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": ['post_office', 'utils'],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [
        # third app for send and manager emails
        "post_office.Attachment",
        "post_office.EmailTemplate",

        # thirthird-part django-extensions - the background
        # and schedule tasks manager
        "django_celery_beat.SolarSchedule",
        "django_celery_beat.IntervalSchedule",
        "django_celery_beat.ClockedSchedule",
        "django_celery_beat.CrontabSchedule",
    ],

    # ícones no sidebar para cada model/link
    "icons": {
        # django default user app
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",

        # notification app
        "notification.Email": "fas fa-at",
        "notification.SMS": "fas fa-comment-dots",
        "notification.Telegram": "fas fa-paper-plane",

        # config app
        # "config.Setting": "fas fa-sliders-h",
        # "config.Site": "fas fa-border-none",

        # third-part django-extensions - the background
        # and schedule tasks manager and task results
        "django_celery_results.GroupResult": "fas fa-server",
        "django_celery_results.TaskResult": "fas fa-server",
        "django_celery_beat.PeriodicTask": "fas fa-server",
    },

    # List of apps (and/or models) to base side menu ordering off of (does not
    # need to contain all apps/models)
    "order_with_respect_to": [
        #------------------------------------------
        "notification",
        "notification.Email",
        "notification.SMS",
        "notification.Telegram",
        #------------------------------------------
        "auth",
        "auth.Groups",
        "auth.Users",
        #------------------------------------------
        # "config",
        # "config.Site",
        # "config.Setting",
        #------------------------------------------
        # third-part django-extensions
        "django_celery_results",
    ],

    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts
    # (must be present in static files)
    "custom_css": '/css/customize_admin.css',
    "custom_js": '/js/customize_admin.js',

    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": True,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs
    "changeform_format": "horizontal_tabs",

    "theme": "minty"
}


# A list of people who get code error notifications
# https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-ADMINS

ADMINS = [
    ('Webmaster', get_env('WEBMASTER_EMAIL')),
]


# settings by runtime env
# logging

create_file(LOG_DIR + '/application-debug.log', "")

if ENVIRONMENT in ['production', 'teste']:
    # The application log handlers
    # https://docs.djangoproject.com/en/4.0/topics/logging/
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': LOG_DIR + '/application-debug.log',
            },
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'suspicious_log': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': LOG_DIR + '/suspicious-request.log',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True,
            },
            'django.request': {
                'handlers': ['file'],
                'level': 'ERROR',
                'propagate': True,
            },
            'django.security.DisallowedHost': {
                'handlers': ['suspicious_log'],
                'level': 'ERROR',
                'propagate': False,
            },
        }
    }
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': LOG_DIR + '/application-debug.log',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }


# cache
# https://docs.djangoproject.com/en/4.0/topics/cache

if ENVIRONMENT in ['production', 'teste']:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
            'LOCATION': '127.0.0.1:11211',
        },
        'staticfiles': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'staticfiles-filehashes'
        }
    }


# sentry
# https://sentry.io/for/django/

if ENVIRONMENT in ['production']:
    from application import sentry
