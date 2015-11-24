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

#For deploying CitizenGrid on MAC OS, uncomment the below line
#ISO_GENERATOR_EXE = '/media/isocreator/cg_vams_iso_gen_mac'
#For deploying CitizenGrid on Linux, uncomment the below line
ISO_GENERATOR_EXE = '/media/isocreator/cg_vams_iso_gen'

# KEY PATH FOR VMCP SIGNING
VMCP_KEY_PATH = os.path.join(PROJECT_ROOT, 'settings', 'cyberlab.doc.ic.ac.uk-cernvmwebapi_rsa.pem')