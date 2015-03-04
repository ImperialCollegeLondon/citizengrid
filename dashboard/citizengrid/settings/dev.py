from base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'citizengridDB',                      # Or path to database file if using sqlite3.
        'USER': 'citizengrid',                      # Not used with sqlite3.
        'PASSWORD': 'xxxxxxx',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
}
}
