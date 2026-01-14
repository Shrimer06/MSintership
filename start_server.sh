#!/bin/bash
# 统一HTTP服务启动脚本

echo "正在启动统一HTTP服务..."
echo ""

# 检查依赖
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3"
    exit 1
fi

# 安装依赖（如果需要）
if [ "$1" == "--install" ]; then
    echo "安装Python依赖..."
    pip3 install -r requirements.txt
    echo ""
fi

# 设置端口
PORT=${PORT:-8888}

# 检查端口是否被占用
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "警告: 端口 $PORT 已被占用"
    read -p "是否停止占用该端口的进程? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在停止占用端口的进程..."
        lsof -ti:$PORT | xargs kill -9 2>/dev/null
        sleep 1
        echo "✓ 端口已清理"
    else
        echo "请使用其他端口: PORT=<端口号> ./start_server.sh"
        exit 1
    fi
fi

# 启动服务
echo "启动服务，端口: $PORT"
echo ""
export PORT=$PORT
python3 src/app.py
