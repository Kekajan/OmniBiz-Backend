import os

from django.core.management import BaseCommand, call_command

from django.conf import settings


class Command(BaseCommand):
    help = 'Migrate existing database'

    def handle(self, *args, **options):
        from business.models import Business
        business_ids = Business.objects.values_list('pk', flat=True)
        print(business_ids)
        for business_id in business_ids:
            db_name = f"{business_id}{os.getenv('db_name_secondary')}"
            self.migration(db_name)

    def migration(self, db_name):
        new_db_settings = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': db_name,
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
            'TIME_ZONE': 'Asia/Kolkata',
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES', time_zone='+05:30'"
            },
            'CONN_HEALTH_CHECKS': settings.DATABASES['default'].get('CONN_HEALTH_CHECKS', {}),
            'CONN_MAX_AGE': 600,
            'AUTOCOMMIT': True,
        }

        settings.DATABASES[db_name] = new_db_settings

        call_command('migrate', database=db_name)
        return True
