# AWS部署指南

本指南介绍如何在AWS EC2实例上部署Django支付应用。

## 步骤1: 设置EC2实例

1. 登录AWS管理控制台，进入EC2服务
2. 启动新实例，选择Ubuntu Server 20.04 LTS
3. 选择t2.micro实例类型（免费套餐）
4. 配置安全组，允许以下端口:
   - SSH (22)
   - HTTP (80)
   - HTTPS (443)
5. 创建并下载密钥对

## 步骤2: 连接到EC2实例

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip-address
```

## 步骤3: 安装依赖项

```bash
# 更新包列表
sudo apt-get update

# 安装Python和pip
sudo apt-get install -y python3 python3-pip python3-venv

# 安装Git
sudo apt-get install -y git

# 安装Nginx
sudo apt-get install -y nginx

# 启动Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

## 步骤4: 克隆项目代码

```bash
# 创建应用目录
mkdir -p ~/webapps2025
cd ~/webapps2025

# 克隆项目代码
git clone https://github.com/your-username/webapps2025.git .
```

## 步骤5: 设置Python环境

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖项
pip install -r requirements.txt

# 安装Gunicorn
pip install gunicorn
```

## 步骤6: 配置应用程序

```bash
# 迁移数据库
python manage.py migrate

# 创建超级用户(如果需要)
python manage.py create_admin

# 收集静态文件
python manage.py collectstatic --noinput
```

## 步骤7: 配置Gunicorn

创建Gunicorn服务文件:

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

添加以下内容:

```
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/webapps2025
ExecStart=/home/ubuntu/webapps2025/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/webapps2025/webapps2025.sock webapps2025.wsgi:application

[Install]
WantedBy=multi-user.target
```

启动Gunicorn:

```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

## 步骤8: 配置Nginx

创建Nginx配置文件:

```bash
sudo nano /etc/nginx/sites-available/webapps2025
```

添加以下内容:

```
server {
    listen 80;
    server_name your-ec2-domain-or-ip;

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

启用站点配置:

```bash
sudo ln -s /etc/nginx/sites-available/webapps2025 /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## 步骤9: 配置SSL (HTTPS)

```bash
# 安装Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-ec2-domain
```

## 步骤10: 测试部署

访问你的域名或IP地址，应该可以看到应用程序运行。

## 部署截图记录

在部署过程中，请记得截取以下内容的截图:

1. EC2实例控制台
2. SSH连接命令
3. 运行迁移命令
4. Gunicorn和Nginx配置
5. 运行中的应用程序（浏览器显示）

这些截图将作为作业提交的一部分。 