import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_HOST = "127.0.0.1"
DB_PASSWORD = "Pass2020!"
DB_USER = "postgres"
DB_PORT = 5432

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'yourdatabasename.db'),
    }
}

INSTALLED_APPS = ("db",)


# SECURITY WARNING: Modify this secret key if using in production!
SECRET_KEY = "6few3nci_q_o@l1dlbk81%wcxe!*6r29yu629&d97!hiqat9fa"

USE_TZ = True
