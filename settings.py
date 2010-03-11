import sys, os
relative_path = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('', ''),
)
MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'busylissy.db'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

TIME_ZONE = 'Europe/Amsterdam'
LANGUAGE_CODE = 'en-us'

gettext = lambda s: s
LANGUAGES = (
    ('en', gettext('English')),
    ('nl', gettext('Dutch')),
)

SITE_ID = 1

USE_I18N = True

MEDIA_ROOT = relative_path('media')
MEDIA_URL = 'http://localhost:8000/media/'

ADMIN_MEDIA_PREFIX = '/media/admin/'

SECRET_KEY = '9*1^o17$q*3f*a63gc)pavb+8h3nf#$&)tcx5_a2n^u^kgxf!c'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django_authopenid.context_processors.authopenid',
    'busylizzy.blprofile.context_processors.settings',
)

MIDDLEWARE_CLASSES = (
    'localeurl.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_authopenid.middleware.OpenIDMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'busylizzy.urls'

TEMPLATE_DIRS = (
    relative_path('templates')
)

INSTALLED_APPS = (
    'localeurl',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.comments',
    'django_authopenid',
    'registration',
    'sorl.thumbnail',
    'tagging',
    'authority',
    'busylizzy.blactivity',
    'busylizzy.blprofile',
    'busylizzy.blgroup',
    'busylizzy.blproject',
    'busylizzy.bltask',
    'busylizzy.blfile',
    'busylizzy.blmessage',
    'busylizzy.blinvite',
    'busylizzy.blagenda',
)

LOGIN_REDIRECT_URL = '/projects/'
LOGIN_URL = '/account/signin/'
ACCOUNT_ACTIVATION_DAYS = 30

AUTH_PROFILE_MODULE = 'blprofile.UserProfile'
AVATAR_SIZE = 60
AVATAR_THUMBNAIL_SIZE = 36

DISALLOWED_PROJECTS = ('hold', 'active', 'finished')
FORCE_LOWERCASE_TAGS = True

EMAIL_NOTIFICATIONS = True
