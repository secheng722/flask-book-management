#!/bin/bash

# 检查虚拟环境是否存在，不存在则直接退出
if [ ! -d ".venv" ]; then
    echo "错误：虚拟环境不存在。请先创建虚拟环境："
    exit 1
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "确保所有依赖已安装..."
uv pip install -r requirements.txt

# 设置环境变量
export SECRET_KEY="YourSecretKeyHere"
export DB_USER="YourDBUserHere"
export DB_PASSWORD="YourDBPasswordHere"
export DB_HOST="YourDBHostHere"
export DB_PORT="3306"
export DB_NAME="bookmanagement"

# 启动应用程序
echo "正在启动Flask应用..."
echo "应用将在80端口运行 - 访问地址：http://服务器IP:80"
# 使用Flask内置服务器启动应用，绑定到所有接口，允许从外部访问
python run.py