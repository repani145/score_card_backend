from django.apps import AppConfig
# from app import signals


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    def ready(self):
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('signals')

