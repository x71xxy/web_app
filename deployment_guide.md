# AWS 部署指南

## 前期准备

1. AWS账户设置
   - 登录AWS Academy
   - 确保有足够的免费额度

2. 本地环境准备
   - 安装AWS CLI
   - 配置Python环境（Python 3.8+）
   - 准备requirements.txt

3. 项目准备
   - 确保所有测试通过
   - 更新settings.py中的生产环境设置
   - 准备静态文件

## 部署步骤

### 1. 创建EC2实例

1. 登录AWS控制台
2. 创建EC2实例：
   - 选择 Ubuntu Server 20.04 LTS
   - 选择 t2.micro (免费套餐)
   - 配置安全组：
     - 允许SSH (端口22)
     - 允许HTTP (端口80)
     - 允许HTTPS (端口443)
   - 创建新密钥对并下载.pem文件

### 2. 连接到EC2实例

```bash
# 修改密钥文件权限
chmod 400 your-key.pem

# SSH连接到实例
ssh -i your-key.pem ubuntu@your-ec2-public-dns
```

### 3. 设置服务器环境

```bash
# 更新包管理器
sudo apt update
sudo apt upgrade -y

# 安装必要的包
sudo apt install -y python3-pip python3-venv nginx

# 创建项目目录
mkdir ~/webapps2025
cd ~/webapps2025

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate
```

### 4. 部署项目代码

1. 在本地打包项目：
```bash
# 在本地项目目录执行
zip -r webapps2025.zip . -x "venv/*" "*.git/*"
```

2. 上传到EC2：
```bash
scp -i your-key.pem webapps2025.zip ubuntu@your-ec2-public-dns:~/webapps2025/
```

3. 在EC2上解压并安装依赖：
```bash
cd ~/webapps2025
unzip webapps2025.zip
pip install -r requirements.txt
```

### 5. 配置Gunicorn

1. 安装Gunicorn：
```bash
pip install gunicorn
```

2. 创建Gunicorn服务文件：
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

添加以下内容：
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/webapps2025
ExecStart=/home/ubuntu/webapps2025/venv/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/webapps2025/webapps2025.sock webapps2025.wsgi:application

[Install]
WantedBy=multi-user.target
```

3. 启动Gunicorn：
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### 6. 配置Nginx

1. 创建Nginx配置文件：
```bash
sudo nano /etc/nginx/sites-available/webapps2025
```

添加以下内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/ubuntu/webapps2025;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/webapps2025/webapps2025.sock;
    }
}
```

2. 启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/webapps2025 /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 7. 配置SSL（HTTPS）

1. 安装Certbot：
```bash
sudo apt install -y certbot python3-certbot-nginx
```

2. 获取SSL证书：
```bash
sudo certbot --nginx -d your-domain.com
```

### 8. 最终检查

1. 更新settings.py中的生产环境设置：
   - DEBUG = False
   - ALLOWED_HOSTS = ['your-domain.com']
   - 确保所有安全设置已启用

2. 收集静态文件：
```bash
python manage.py collectstatic
```

3. 应用数据库迁移：
```bash
python manage.py migrate
```

4. 重启服务：
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

## 监控和维护

1. 检查日志：
```bash
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u gunicorn
```

2. 系统更新：
```bash
sudo apt update
sudo apt upgrade
```

3. 备份数据库：
```bash
python manage.py dumpdata > backup.json
```

## 故障排除

1. 检查服务状态：
```bash
sudo systemctl status nginx
sudo systemctl status gunicorn
```

2. 检查权限：
```bash
sudo chown -R ubuntu:www-data /home/ubuntu/webapps2025
```

3. 检查防火墙：
```bash
sudo ufw status
```

## 安全建议

1. 定期更新系统和依赖包
2. 使用强密码
3. 限制SSH访问
4. 配置防火墙
5. 启用HTTPS
6. 定期备份数据

## 部署后检查清单

- [ ] 网站可以通过HTTPS访问
- [ ] 静态文件正确加载
- [ ] 数据库迁移成功
- [ ] 用户注册和登录功能正常
- [ ] 支付功能正常工作
- [ ] 管理员界面可访问
- [ ] 日志正确记录
- [ ] 备份系统正常工作 