# PostgreSQL 数据库配置和迁移指南

本指南将帮助您将应用程序从 SQLite 迁移到 PostgreSQL 数据库。

## 先决条件

1. 已安装 PostgreSQL 数据库服务器
2. 已安装 Python 和 Django
3. 已安装 psycopg2 (PostgreSQL 的 Python 适配器)

## 第一步：安装 PostgreSQL

### Windows
1. 从 [PostgreSQL 官方网站](https://www.postgresql.org/download/windows/) 下载并安装 PostgreSQL
2. 在安装过程中设置 postgres 用户密码，并记住该密码
3. 安装 pgAdmin (可选，但推荐) 作为图形化管理工具

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'your-password';"
```

### macOS
```bash
brew install postgresql
brew services start postgresql
```

## 第二步：创建数据库

1. 登录到 PostgreSQL：
```bash
psql -U postgres
```

2. 创建数据库：
```sql
CREATE DATABASE webapps2025;
```

3. 退出 psql：
```
\q
```

## 第三步：配置 Django 设置

1. 确保已安装必要的依赖：
```bash
pip install psycopg2-binary python-dotenv
```

2. 配置 `.env` 文件（已在项目根目录创建）：
```
DB_NAME=webapps2025
DB_USER=postgres
DB_PASSWORD=your-strong-password-here
DB_HOST=localhost
DB_PORT=5432
```

3. 更新 `settings.py` 以使用 PostgreSQL（已完成）

## 第四步：迁移数据

1. 运行迁移脚本：
```bash
python migrate_to_postgres.py
```

2. 按照脚本提示完成迁移过程。

## 第五步：验证迁移

1. 启动 Django 开发服务器：
```bash
python manage.py runserver
```

2. 登录应用程序并验证所有数据已正确迁移

## 常见问题解决

### 连接错误
- 确保 PostgreSQL 服务正在运行
- 验证用户名和密码是否正确
- 检查主机和端口设置
- 确保 PostgreSQL 配置允许连接（pg_hba.conf）

### 迁移问题
- 如果遇到迁移错误，尝试运行：`python manage.py migrate --fake-initial`
- 对于模型冲突，可能需要手动解决迁移文件中的冲突

### 性能优化
- 添加适当的索引
- 针对大型表进行优化查询
- 考虑使用连接池

## 生产环境部署

在生产环境中，建议：
1. 使用单独的数据库服务器或托管服务（如 AWS RDS）
2. 配置适当的备份策略
3. 设置数据库复制
4. 实施适当的安全措施，如强密码和防火墙规则

## 相关资源

- [Django 文档：数据库设置](https://docs.djangoproject.com/en/4.2/ref/settings/#databases)
- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [psycopg2 文档](https://www.psycopg.org/docs/) 