from base import *

SOUTH_TESTS_MIGRATE = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_ROOT, '..', 'citizengrid_test.db'), # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#For deploying CitizenGrid on MAC OS, uncomment the below line
#ISO_GENERATOR_EXE = '/media/isocreator/cg_vams_iso_gen_mac'
#For deploying CitizenGrid on Linux, uncomment the below line
ISO_GENERATOR_EXE = '/media/isocreator/cg_vams_iso_gen'
