from base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_ROOT, '..', 'citizengrid.db'), # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#For deploying CitizenGrid on MAC OS, uncomment the below line
ISO_GENERATOR_EXE = '/media/isocreator/cg_vams_iso_gen_mac'
#For deploying CitizenGrid on Linux, uncomment the below line
#ISO_GENERATOR_EXE = '/media/isocreator/cg_vams_iso_gen'

# KEY PATH FOR VMCP SIGNING
VMCP_KEY_PATH = os.path.join(PROJECT_ROOT, 'settings', 'test-local.pem')

HTTP_PORT = 8000
HTTPS_PORT = 8000