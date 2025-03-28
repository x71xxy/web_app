from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal
from register.models import UserProfile
from payapp.models import Account

class Command(BaseCommand):
    help = '创建默认管理员用户 (admin1)'

    def handle(self, *args, **kwargs):
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
                    
                    self.stdout.write(self.style.SUCCESS('Successfully created admin user: admin1'))
            else:
                self.stdout.write(self.style.SUCCESS('Admin user already exists'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error creating admin user: {e}')) 