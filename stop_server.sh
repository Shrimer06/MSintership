#!/bin/bash
# 停止统一HTTP服务脚本

echo "正在停止服务..."

# 查找并关闭占用端口的进程
for port in 5000 5001 8888; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo "发现端口 $port 被进程 $pid 占用，正在关闭..."
        kill -9 $pid 2>/dev/null
        sleep 1
    fi
done

# 查找并关闭所有python src/app.py进程
pkill -f "python.*src/app.py" 2>/dev/null

echo "✓ 服务已停止"
