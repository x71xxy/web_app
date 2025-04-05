# WebApps2025 支付应用

一个基于 Django 的现代化支付应用程序，支持多种货币、用户认证、支付请求和交易历史记录。

## 功能特点

- 用户注册和认证
- 账户管理
- 多货币支持和汇率转换
- 发送和接收支付
- 支付请求
- 交易历史记录
- 通知系统
- 管理员仪表板

## 技术栈

- Django 4.2.7
- PostgreSQL 数据库
- Bootstrap 5 (前端框架)
- Django Crispy Forms
- 使用 .env 文件管理环境变量

## 安装和设置

### 先决条件

- Python 3.8+
- PostgreSQL 数据库
- pip (Python 包管理器)

### 步骤

1. 克隆仓库：
```bash
git clone https://github.com/your-username/webapps2025.git
cd webapps2025
```

2. 创建并激活虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # 在 Windows 上使用: venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置数据库：
   - 按照 [PostgreSQL 数据库配置](#postgresql-数据库配置) 部分的说明设置 PostgreSQL

5. 设置环境变量：
   - 复制 `.env.example` 文件为 `.env`
   - 编辑 `.env` 文件，填写必要的设置

6. 运行迁移：
```bash
python manage.py migrate
```

7. 创建超级用户：
```bash
python manage.py createsuperuser
```

8. 启动开发服务器：
```bash
python manage.py runserver
```

9. 访问应用程序：
   - 打开浏览器，访问 http://127.0.0.1:8000/

## PostgreSQL 数据库配置

应用程序默认使用 PostgreSQL 作为数据库。请按照以下步骤设置：

1. 安装 PostgreSQL（如果尚未安装）：
   - [Windows 安装指南](https://www.postgresql.org/download/windows/)
   - [macOS 安装指南](https://www.postgresql.org/download/macosx/)
   - [Linux 安装指南](https://www.postgresql.org/download/linux/)

2. 创建数据库：
```sql
CREATE DATABASE webapps2025;
```

3. 在 `.env` 文件中配置数据库连接：
```
DB_NAME=webapps2025
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

4. 如果从 SQLite 迁移到 PostgreSQL，请运行迁移脚本：
```bash
python migrate_to_postgres.py
```

详细的迁移说明请参考 [README_POSTGRES.md](README_POSTGRES.md) 文件。

## 部署说明

应用程序可以部署到 AWS EC2、Heroku 或其他云服务提供商。

### EC2 部署

1. 在 EC2 实例上安装必要的软件包
2. 克隆仓库并安装依赖
3. 设置 PostgreSQL 数据库
4. 配置 Nginx 和 Gunicorn
5. 设置 SSL/TLS 证书

详细的部署说明请参考 `docs/deployment.md` 文件。

## 开发

### 代码风格

- 遵循 PEP 8 编码规范
- 使用 Django 的 MVT 架构模式
- 为所有功能编写测试

### 测试

运行测试：
```bash
python manage.py test
```

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 文件了解详情。

## 许可证

此项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请联系：your-email@example.com 