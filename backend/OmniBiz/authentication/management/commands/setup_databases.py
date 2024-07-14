# authentication/management/commands/setup_databases.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import router, connections
from contextlib import contextmanager


class Command(BaseCommand):
    help = 'Setup databases and run initial migrations'

    def handle(self, *args, **kwargs):
        call_command('migrate', database='default')
