# -*- coding: utf-8 -*-
# Django settings for GeoNode project.
from urllib import urlencode
import os

_ = lambda x: x

DEBUG = True
SITENAME = "GeoNode"
SITEURL = "http://localhost:8000/"
TEMPLATE_DEBUG = DEBUG

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = os.path.join(PROJECT_ROOT,"..","..","..","development.db")
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Not used with sqlite3.
DATABASE_PORT = ''             # Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', 'English'),
    ('es', 'Español'),
    ('it', 'Italiano'),
    ('fr', 'Français'),
)

SITE_ID = 1

# Setting a custom test runner to avoid running the tests for some problematic 3rd party apps
TEST_RUNNER='django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
      '--verbosity=2',
      '--cover-erase',
      '--nocapture',
      '--with-coverage',
      '--cover-package=geonode',
      '--cover-inclusive',
      '--cover-tests',
      '--detailed-errors',
      '--with-xunit',

# This is very beautiful/usable but requires: pip install rudolf
#      '--with-color',

# The settings below are useful while debugging test failures or errors

#      '--failed',
#      '--pdb-failures',
#      '--stop',
#      '--pdb',
      ]

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "site_media", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/site_media/media/"

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "site_media", "static")

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = "/media/"

# Additional directories which hold static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "media"),
]

GEONODE_UPLOAD_PATH = os.path.join(STATIC_URL, "upload/")

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = os.path.join(STATIC_URL, "admin/")

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'myv-y4#7j-d*p-__@j#*3z@!y24fz8%^z2v6atuy4bo9vqr1_a'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    #'django.template.loaders.eggs.load_template_source',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "geonode.maps.context_processors.resource_urls",
    "django.core.context_processors.request",
    "notification.context_processors.notification",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'cbv.middleware.DeferredRenderingMiddleware',
)

# This isn't required for running the geonode site, but it when running sites that inherit the geonode.settings module.
LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, "locale"),
    os.path.join(PROJECT_ROOT, "maps", "locale"),
)

ROOT_URLCONF = 'geonode.urls'

# Note that Django automatically includes the "templates" dir in all the
# INSTALLED_APPS, se there is no need to add maps/templates or admin/templates
TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT,"templates"),    
)

# The FULLY QUALIFIED url to the GeoServer instance for this GeoNode.
GEOSERVER_BASE_URL = "http://localhost:8001/geoserver/"

# Default password for the geoserver admin user, autogenerated during bootstrap
#GEOSERVER_TOKEN = open(os.path.join(PROJECT_ROOT,"..","..", "..","geoserver_token")).readline()[0:-1]

# The username and password for a user that can add and edit layer details on GeoServer
GEOSERVER_CREDENTIALS = "admin", "@dm1n"

# The FULLY QUALIFIED url to the GeoNetwork instance for this GeoNode
GEONETWORK_BASE_URL = "http://localhost:8001/geonetwork/"

# The username and password for a user with write access to GeoNetwork
GEONETWORK_CREDENTIALS = "admin", "admin"

AUTHENTICATION_BACKENDS = ('geonode.core.auth.GranularBackend',)

GOOGLE_API_KEY = "ABQIAAAAkofooZxTfcCv9Wi3zzGTVxTnme5EwnLVtEDGnh-lFVzRJhbdQhQgAhB1eT_2muZtc0dl-ZSWrtzmrw"
LOGIN_REDIRECT_URL = "/"

DEFAULT_LAYERS_OWNER='admin'

# Where should newly created maps be focused?
DEFAULT_MAP_CENTER = (-84.7, 12.8)

# How tightly zoomed should newly created maps be?
# 0 = entire world;
# maximum zoom is between 12 and 15 (for Google Maps, coverage varies by area)
DEFAULT_MAP_ZOOM = 7

DEFAULT_LAYER_SOURCE = {
    "ptype":"gxp_wmscsource",
    "url":"/geoserver/wms",
    "restUrl": "/gs/rest"
}

MAP_BASELAYERS = [{
    "source": {"ptype": "gx_olsource"},
    "type":"OpenLayers.Layer",
    "args":["No background"],
    "visibility": False,
    "fixed": True,
    "group":"background"
  },{
    "source": { "ptype":"gx_olsource"},
    "type":"OpenLayers.Layer.OSM",
    "args":["OpenStreetMap"],
    "visibility": True,
    "fixed": True,
    "group":"background"
  },{
    "source": {"ptype":"gx_olsource"},
    "type":"OpenLayers.Layer.WMS",
    "group":"background",
    "visibility": False,
    "fixed": True,
    "args":[
      "bluemarble",
      "http://maps.opengeo.org/geowebcache/service/wms",
      {
        "layers":["bluemarble"],
        "format":"image/png",
        "tiled": True,
        "tilesOrigin":[-20037508.34,-20037508.34]
      },
      {"buffer":0}
    ]

}]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.sitemaps',

    
    'staticfiles',
    'django_extensions',
    'registration',
    'idios',
    'avatar',

    'agon_ratings',
    'dialogos',
    'taggit',
    'relationships',
    'announcements',
    'notification',
    'actstream',
    'user_messages',
    'crispy_forms',
    'haystack',
    'south',
    
    'geonode.core',
    'geonode.maps',
    'geonode.people',
    'geonode.proxy',
    'geonode.groups',
    'geonode'
)

# List of models that actstream can take action on.
ACTSTREAM_ACTION_MODELS = [
        "auth.User",
        "groups.Group",
]

def get_user_url(u):
    from django.contrib.sites.models import Site
    s = Site.objects.get_current()
    return "http://" + s.domain + "/profiles/profile" + u.username


ABSOLUTE_URL_OVERRIDES = {
    'auth.user': get_user_url
}

AUTH_PROFILE_MODULE = 'people.Contact'
REGISTRATION_OPEN = False

SERVE_MEDIA = DEBUG;

STATICFILES_FINDERS = [
    'staticfiles.finders.FileSystemFinder',
    'staticfiles.finders.AppDirectoriesFinder',
    'staticfiles.finders.LegacyAppDirectoriesFinder'
]

#GEONODE_CLIENT_LOCATION = "http://localhost:8001/geonode-client/"
GEONODE_CLIENT_LOCATION = "/media/static/"

#Import uploaded shapefiles into a database such as PostGIS?
DB_DATASTORE=False

#Database datastore connection settings
DB_DATASTORE_NAME = ''
DB_DATASTORE_USER = ''
DB_DATASTORE_PASSWORD = ''
DB_DATASTORE_HOST = ''
DB_DATASTORE_PORT = ''
DB_DATASTORE_TYPE=''

# Agon Ratings
AGON_RATINGS_CATEGORY_CHOICES = {
    "maps.Map": {
        "map": "How good is this map?"
    },
    "maps.Layer": {
        "layer": "How good is this layer?"
    },
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}

try:
    from local_settings import *
except ImportError:
    pass

