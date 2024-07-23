# Utils/Database/Generate_Database/Dynamic_Database.py
from django.core.management.base import BaseCommand
from django.db import connection, router
from django.conf import settings
from contextlib import contextmanager


class DynamicDatabaseCreationCommand(BaseCommand):
    help = 'Create and migrate a dynamic database'

    def add_arguments(self, parser):
        parser.add_argument('dbname', type=str, help='The name of the new dynamic database')

    def handle(self, *args, **options):
        dbname = options['dbname']
        self.create_and_migrate_dynamic_db(dbname)

    def create_and_migrate_dynamic_db(self, dbname):
        new_db_settings = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': dbname,
            'USER': settings.DATABASES['default']['USER'],
            'PASSWORD': settings.DATABASES['default']['PASSWORD'],
            'HOST': settings.DATABASES['default']['HOST'],
            'PORT': settings.DATABASES['default']['PORT'],
        }

        settings.DATABASES[dbname] = new_db_settings

        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbname}")

        # with override_router():
        from django.core.management import call_command
        call_command('migrate', database=dbname)

        return True
