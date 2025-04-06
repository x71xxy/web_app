from django.apps import AppConfig
import os

class RegisterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'register'
    
    def ready(self):
        # Only run in non-test environment
        if os.environ.get('RUN_MAIN', None) != 'true':
            return