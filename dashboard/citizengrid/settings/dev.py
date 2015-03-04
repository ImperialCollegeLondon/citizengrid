# Development settings for CitizenGrid project.
from citizengrid.settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'citizengridDB',                      # Or path to database file if using sqlite3.
        'USER': 'citizengrid',                      # Not used with sqlite3.
        'PASSWORD': 'xxxxxxxx',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
        }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
    #    'mail_admins': {
    #        'level': 'ERROR',
    #        'filters': ['require_debug_false'],
    #        'class': 'django.utils.log.AdminEmailHandler'
    #    },
         'console':{
             'level': 'DEBUG',
             'class': 'logging.StreamHandler',
             'formatter': 'verbose'
         },
    },
    'loggers': {
    'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        #'django.request': {
        #    'handlers': ['mail_admins'],
        #    'level': 'ERROR',
        #    'propagate': True,
        #},
    }
}