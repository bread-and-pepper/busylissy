"""
These are the settings which are only applicable when developing the project
on your own pc. Only settings which are different than the server settings
should be put here.

"""
from settings import *
import sys, os

DEBUG = True
LOCAL_DEVELOPMENT = True
relative_path = lambda x: os.path.join(os.path.abspath(os.path.dirname(__file__)), x)

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'development.db'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'ham@breadandpepper.com'
EMAIL_HOST_PASSWORD = 'broodjepeper'
EMAIL_PORT = 587

MEDIA_ROOT = relative_path('media')
MEDIA_URL = 'http://localhost:8000/media/'

TEMPLATE_DIRS = (
    relative_path('templates')
)
