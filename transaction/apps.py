from django.apps import AppConfig


class TransactionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transaction'

    def ready(self) -> None:
        import transaction.signals
        return super().ready()
