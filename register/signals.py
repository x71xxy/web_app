from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal
from .models import UserProfile
from payapp.models import Account

@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    # 仅在应用的post_migrate信号接收后执行
    if sender.name == 'register':
        try:
            # 检查是否存在admin1用户
            if not User.objects.filter(username='admin1').exists():
                with transaction.atomic():
                    # 创建admin用户
                    admin_user = User.objects.create_user(
                        username='admin1',
                        email='admin1@example.com',
                        password='admin1',
                        first_name='Admin',
                        last_name='User'
                    )
                    
                    # 设置为工作人员和超级用户
                    admin_user.is_staff = True
                    admin_user.is_superuser = True
                    admin_user.save()
                    
                    # 创建用户档案
                    profile = UserProfile.objects.create(
                        user=admin_user,
                        currency='GBP'
                    )
                    
                    # 创建账户，初始余额为750英镑
                    Account.objects.create(
                        user=admin_user,
                        balance=Decimal('750.00'),
                        currency='GBP'
                    )
                    
                    print('Successfully created admin user: admin1')
        except Exception as e:
            print(f"Error creating admin user: {e}") 