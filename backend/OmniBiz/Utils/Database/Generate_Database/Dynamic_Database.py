# Utils/Database/Generate_Database/Dynamic_Database.py
import os
import logging

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings


class DynamicDatabaseCreationCommand(BaseCommand):
    help = 'Create and migrate a dynamic database'

    def add_arguments(self, parser):
        parser.add_argument('dbname', type=str, help='The name of the new dynamic database')

    def handle(self, *args, **options):
        dbname = options['dbname']
        self.create_and_migrate_dynamic_db(dbname)

    def create_and_migrate_dynamic_db(self, business_id):
        dbname = f'{business_id}{os.getenv('DB_NAME_SECONDARY')}'
        logging.info(f'Creating dynamic database: {dbname}')
        new_db_settings = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': dbname,
            'USER': settings.DATABASES['default']['USER'],
            'PASSWORD': settings.DATABASES['default']['PASSWORD'],
            'HOST': settings.DATABASES['default']['HOST'],
            'PORT': settings.DATABASES['default']['PORT'],
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

        settings.DATABASES[dbname] = new_db_settings

        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbname}")

        from django.core.management import call_command
        call_command('migrate', database=dbname)

        return True
