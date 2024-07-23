import logging

from django.apps import AppConfig
from django.core.management import call_command


class BusinessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'business'


