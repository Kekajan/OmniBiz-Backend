from django.apps import AppConfig


class CashBookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cash_book'

    def ready(self):
        import cash_book.signals
