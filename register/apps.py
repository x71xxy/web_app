from django.apps import AppConfig
import os

class RegisterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'register'
    
    def ready(self):
        # 仅在非测试环境下运行
        if os.environ.get('RUN_MAIN', None) != 'true' and not os.environ.get('TESTING'):
            # 导入信号处理器
            from . import signals
        # import register.signals  # 暂时不需要信号处理器
        pass 