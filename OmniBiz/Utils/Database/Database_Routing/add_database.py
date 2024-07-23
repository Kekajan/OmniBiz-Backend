import logging
import os
from django.conf import settings
from django.db import connections
from django.db.utils import ConnectionDoesNotExist


def add_database(database_name):
    if database_name not in settings.DATABASES:
        settings.DATABASES[database_name] = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': database_name,
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
            'ATOMIC_REQUESTS': True,
            'TIME_ZONE': 'Asia/Kolkata',
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES', time_zone='+05:30'"
            },
            'CONN_MAX_AGE': 600,
            'AUTOCOMMIT': True,
            'CONN_HEALTH_CHECKS': False,
        }
    # Ensure the connection is initialized
    try:
        connection = connections[database_name]
        connection.ensure_connection()
    except ConnectionDoesNotExist:
        logging.error(f"Database {database_name} does not exist")
    except Exception as e:
        logging.error(f"Error connecting to database {database_name}: {e}")
