# Flask 图书管理系统

一个使用 Flask 框架开发的图书管理系统，支持用户认证、图书管理、借阅管理等功能。

## 项目功能

- **用户管理**：登录、注册、个人信息修改、密码更改
- **图书管理**：增加、删除、修改、查询图书信息
- **借阅系统**：借书、还书、借阅历史查询
- **管理功能**：管理员可管理用户、图书和借阅记录

## 技术栈

- **后端**：Flask
- **数据库**：MySQL
- **前端**：HTML/CSS/JavaScript
- **依赖管理**：uv (Python 包管理工具)

## 环境要求

- Python 3.8+
- MySQL 5.7+
- 其他依赖见 `requirements.txt`

## 本地安装说明

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd flask-book-management
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # 或
   # .\.venv\Scripts\activate  # Windows
   ```

3. **安装 uv**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
   # 或访问 https://github.com/astral-sh/uv 查看 Windows 安装说明
   ```

4. **安装依赖**
   ```bash
   uv pip install -r requirements.txt
   ```

5. **配置环境变量**
   
   创建 `.env` 文件，包含以下内容：
   ```
   SECRET_KEY=your_secret_key
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=3306
   DB_NAME=bookmanagement
   ```

6. **初始化数据库**
   ```bash
   # 确保 MySQL 服务已启动，并创建数据库
   mysql -u root -p
   > CREATE DATABASE bookmanagement;
   > exit
   
   # 初始化数据库表 (需根据实际情况调整)
   python -c "from app import create_app; from app.models import db; app = create_app(); with app.app_context(): db.create_all()"
   ```

7. **启动应用**
   ```bash
   python run.py
   ```
   
   现在可以通过 http://localhost:5000 访问应用

## AWS 部署说明

该项目设计为在 AWS 云服务上部署，使用 EC2 作为应用服务器，RDS 作为数据库服务器。

1. **创建 EC2 实例**
   - 选择 Amazon Linux 2023 AMI
   - 建议使用 t2.micro/t3.micro 实例类型（免费套餐）
   - **重要**：创建实例时勾选"配置安全组"选项，开放 5000 端口（或 80/443 端口）
   - 创建并下载密钥对（.pem 文件），用于 SSH 连接
   - 记录 EC2 实例的公网 IP 地址

2. **创建 RDS 数据库**
   - 选择 MySQL 引擎
   - 根据需求选择合适的实例类型（可使用 db.t3.micro 免费套餐）
   - 设置数据库名称为 `bookmanagement`
   - 创建主用户凭证（用户名和密码）
   - **注意**：首次创建时会显示密码，请务必保存，后续将无法再次查看
   - 配置 VPC 安全组，允许来自 EC2 实例的连接（端口 3306）
   - 记录 RDS 终端节点（hostname）和凭证

3. **部署应用**
   ```bash
   # 登录到 EC2 实例
   ssh -i your-key.pem ec2-user@your-ec2-ip
   
   # 安装 Git、Python 和其他依赖
   sudo yum update -y
   sudo yum install git python3 python3-pip python3-devel mysql-devel gcc -y
   
   # 安装 uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # 克隆代码
   git clone <repository-url>
   cd flask-book-management
   
   # 创建虚拟环境
   python3 -m venv .venv
   source .venv/bin/activate
   
   # 创建 .env 文件，填入适当配置
   nano .env
   
   # .env 文件示例内容
   # SECRET_KEY=your_secret_key
   # DB_USER=admin
   # DB_PASSWORD=your_rds_password
   # DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
   # DB_PORT=3306
   # DB_NAME=bookmanagement
   
   # 运行启动脚本
   bash start_aws.sh
   ```

4. **配置为系统服务**（可选）
   
   为了确保应用在服务器重启后自动启动，可以将其配置为系统服务：
   ```bash
   sudo nano /etc/systemd/system/flask-book-management.service
   ```
   
   添加以下内容：
   ```ini
   [Unit]
   Description=Flask Book Management System
   After=network.target
   
   [Service]
   User=ec2-user
   WorkingDirectory=/home/ec2-user/flask-book-management
   ExecStart=/bin/bash /home/ec2-user/flask-book-management/start_aws.sh
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   启用服务：
   ```bash
   sudo systemctl enable flask-book-management
   sudo systemctl start flask-book-management
   ```

## 项目结构

```
flask-book-management/
├── app/                  # 应用主目录
│   ├── forms/            # 表单定义
│   ├── models/           # 数据模型
│   ├── static/           # 静态资源
│   ├── templates/        # HTML 模板
│   └── views/            # 路由视图
├── config.py             # 配置文件
├── requirements.txt      # 依赖列表
├── run.py               # 入口文件
└── start_aws.sh         # AWS 部署脚本
```

## 注意事项

1. **安全性考虑**
   - 不要在代码中硬编码敏感信息（如数据库密码）
   - 使用 .env 文件或环境变量存储敏感配置
   - 确保 .env 文件不被提交到版本控制系统

2. **数据库连接**
   - 确保数据库连接字符串中包含正确的字符集设置
   - 针对 RDS，确保安全组允许来自 EC2 实例的连接（端口 3306）
   - RDS 和 EC2 应位于同一 VPC 下，以保证网络互通
   - 使用 RDS 提供的终端节点作为数据库主机名

3. **生产环境建议**
   - 使用 Gunicorn 或 uWSGI 替代 Flask 内置服务器
   - 配置 Nginx 作为反向代理
   - 启用 HTTPS 以保护数据传输安全
   
4. **AWS 特有配置**
   - EC2 安全组需要开放入站规则允许 HTTP/HTTPS 流量
   - RDS 安全组需要允许来自 EC2 安全组或 IP 的 MySQL 连接
   - 使用 IAM 角色管理权限，避免硬编码 AWS 凭证
   - 考虑配置 CloudWatch 监控应用状态

## 许可证

[填写适当的许可证信息]

## 联系方式

[填写联系方式]
