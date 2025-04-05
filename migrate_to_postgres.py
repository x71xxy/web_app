#!/usr/bin/env python
"""
迁移脚本：将数据从 SQLite 迁移到 PostgreSQL
使用方法：
1. 确保已安装 Django, PostgreSQL 和必要的依赖
2. 创建 PostgreSQL 数据库
3. 配置好 .env 文件
4. 运行此脚本: python migrate_to_postgres.py
"""

import os
import sys
import django
import subprocess
import time

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapps2025.settings')
django.setup()

def run_command(command):
    """运行 shell 命令并打印输出"""
    print(f"执行命令: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stdout:
        print(f"输出: {stdout.decode()}")
    if stderr:
        print(f"错误: {stderr.decode()}")
    return process.returncode

def main():
    print("开始数据库迁移过程...")
    
    # 确保 PostgreSQL 数据库已创建
    print("\n1. 确保 PostgreSQL 数据库已创建")
    from django.conf import settings
    db_name = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    
    print(f"将使用以下数据库配置：")
    print(f"数据库名称: {db_name}")
    print(f"用户: {db_user}")
    print(f"主机: {db_host}")
    print(f"端口: {db_port}")
    
    # 迁移前备份 SQLite 数据库
    print("\n2. 备份当前的 SQLite 数据库")
    sqlite_backup = "webapps_backup_" + time.strftime("%Y%m%d_%H%M%S") + ".db"
    import shutil
    try:
        shutil.copy2('webapps.db', sqlite_backup)
        print(f"SQLite 数据库已备份为 {sqlite_backup}")
    except Exception as e:
        print(f"备份 SQLite 数据库时出错: {e}")
        return
    
    # 创建新的迁移文件
    print("\n3. 生成迁移文件")
    run_command("python manage.py makemigrations")
    
    # 应用迁移到 PostgreSQL
    print("\n4. 将迁移应用到 PostgreSQL")
    run_command("python manage.py migrate")
    
    # 将数据从 SQLite 导出到 JSON
    print("\n5. 将数据从 SQLite 导出到 JSON")
    # 临时修改设置以连接到 SQLite
    from django.db import connections
    old_db = settings.DATABASES['default'].copy()
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(settings.BASE_DIR, 'webapps.db'),
    }
    
    # 关闭所有数据库连接
    for conn in connections.all():
        conn.close()
    
    # 导出数据
    run_command("python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data_dump.json")
    
    # 恢复原始数据库设置
    settings.DATABASES['default'] = old_db
    for conn in connections.all():
        conn.close()
    
    # 将数据导入到 PostgreSQL
    print("\n6. 将数据导入到 PostgreSQL")
    run_command("python manage.py loaddata data_dump.json")
    
    print("\n7. 创建超级用户（如果需要）")
    create_superuser = input("是否创建新的超级用户？ (y/n): ")
    if create_superuser.lower() == 'y':
        run_command("python manage.py createsuperuser")
    
    print("\n迁移完成！")
    print("请检查数据是否已正确迁移。")
    print("如果一切正常，您可以删除以下文件：")
    print(f"- {sqlite_backup} (SQLite 备份)")
    print("- data_dump.json (数据转储文件)")

if __name__ == "__main__":
    main() 