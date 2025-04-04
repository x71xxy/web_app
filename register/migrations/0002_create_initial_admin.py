# Generated by Django 5.1.7 on 2025-03-17 19:18

from django.db import migrations
from django.db import transaction
from django.contrib.auth.hashers import make_password

def create_initial_admin(apps, schema_editor):
    # 通过apps获取模型，而不是直接导入
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('register', 'UserProfile')
    Account = apps.get_model('payapp', 'Account')
    
    # 检查是否已存在管理员用户
    if User.objects.filter(username='admin1').count() == 0:
        with transaction.atomic():
            # 创建管理员用户
            admin = User.objects.create(
                username='admin1',
                email='admin1@example.com',
                password=make_password('admin1'),  # 使用make_password加密密码
                first_name='Admin',
                last_name='User',
                is_staff=True,
                is_superuser=True
            )
            
            # 创建用户配置文件
            user_profile = UserProfile.objects.create(
                user_id=admin.id, 
                currency='GBP'
            )
            
            # 创建账户
            Account.objects.create(
                user_id=admin.id,
                balance=750.00,
                currency='GBP'
            )

def reverse_initial_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='admin1').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('register', '0001_initial'),
        ('payapp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_admin, reverse_initial_admin),
    ]
