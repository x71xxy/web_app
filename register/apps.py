from django.apps import AppConfig
import os

class RegisterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'register'
    
    def ready(self):
        # 仅在非测试环境下运行
        if os.environ.get('DJANGO_SETTINGS_MODULE') != 'webapps2025.settings.test':
            # 导入信号处理器
            from . import signals
        # import register.signals  # 暂时不需要信号处理器
        pass 