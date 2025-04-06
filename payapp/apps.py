from django.apps import AppConfig

class PayappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payapp'
    
    # import payapp.signals  # Not needed for now
    
    def ready(self):
        # import payapp.signals  # Not needed for now
        pass 