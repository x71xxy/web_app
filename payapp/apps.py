from django.apps import AppConfig

class PayappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payapp'
    
    def ready(self):
        # import payapp.signals  # 暂时不需要信号处理器
        pass 