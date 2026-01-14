# 问题修复说明

## 已修复的问题

### 1. 端口占用问题 ✅

**问题描述**:
- 多个后台进程尝试启动服务，导致端口冲突
- 端口5000、5001、8888被占用

**解决方案**:
- 创建了 `stop_server.sh` 脚本来清理所有占用端口的进程
- 更新了 `start_server.sh` 脚本，添加端口检查和自动清理功能

**使用方法**:
```bash
# 停止所有服务
./stop_server.sh

# 启动服务（会自动检查端口）
./start_server.sh

# 使用指定端口启动
PORT=9000 ./start_server.sh
```

---

### 2. 证券查询HTTP 567错误 ⚠️

**问题描述**:
- 在完整查询时，查询到第30个人员后开始出现HTTP 567错误
- 这是由于请求过于频繁触发了反爬虫机制

**原因分析**:
1. 完整查询需要对每个匹配人员逐个查询详情
2. 每次查询间隔2秒，但查询50个人员仍然可能触发限制
3. HTTP 567是自定义错误，通常表示触发了反爬虫或IP限制

**解决方案**:
- 建议使用单独的搜索和详情查询接口，而不是完整查询
- 如果必须使用完整查询，建议：
  - 增加延迟时间（修改`sleep_time`参数）
  - 限制一次查询的人员数量
  - 添加重试机制

**推荐用法**:
```bash
# 推荐：先搜索，获取UUID
curl "http://localhost:8888/api/sac/search?name=李明"

# 然后只查询需要的人员详情
curl -X POST http://localhost:8888/api/sac/detail \
  -H "Content-Type: application/json" \
  -d '{"uuid": "<UUID>"}'

# 不推荐：完整查询（可能会触发反爬虫）
# curl "http://localhost:8888/api/sac/full?name=李明"
```

---

### 3. 后台进程管理 ✅

**问题描述**:
- 测试时留下了多个后台进程未清理

**解决方案**:
- 创建了 `stop_server.sh` 脚本统一管理进程
- 脚本会自动查找并关闭所有相关进程

---

## 当前系统状态

### ✅ 正常功能
- 健康检查 (`/health`)
- 证券人员搜索 (`/api/sac/search`)
- 证券人员详情查询 (`/api/sac/detail`)
- PDF下载 (`/api/pdf/download`)

### ⚠️ 需注意功能
- 证券完整查询 (`/api/sac/full`) - 查询大量人员时可能触发反爬虫

---

## 快速开始指南

### 1. 停止所有服务
```bash
./stop_server.sh
```

### 2. 启动服务
```bash
# 使用默认端口8888
./start_server.sh

# 或指定其他端口
PORT=9000 ./start_server.sh
```

### 3. 测试服务
```bash
# 健康检查
curl http://localhost:8888/health

# 证券查询
curl "http://localhost:8888/api/sac/search?name=张伟"

# PDF下载（需要替换为真实的PDF URL）
curl -X POST http://localhost:8888/api/pdf/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/file.pdf"}' \
  --output test.pdf
```

---

## 故障排查

### 问题1: 端口已被占用
```bash
# 查看占用端口的进程
lsof -ti:8888

# 停止占用端口的进程
./stop_server.sh
```

### 问题2: 证券查询返回空结果
- 检查姓名是否存在
- 确认网络连接正常
- 查看服务日志是否有错误

### 问题3: PDF下载失败
- 确认PDF URL可访问
- 检查Chrome浏览器是否已安装
- 查看服务日志获取详细错误信息

### 问题4: 查看服务日志
服务日志会实时输出到终端，包含：
- 请求详情
- 查询状态
- 错误信息

---

## 性能优化建议

### 1. 证券查询优化
```python
# 在 src/services/sac_service.py 中调整延迟时间
sac_client = SACPersonAPI(headless=True, sleep_time=3)  # 增加到3秒
```

### 2. 添加缓存
考虑添加Redis缓存来缓存查询结果，减少重复请求。

### 3. 使用代理
如果需要大量查询，建议使用代理IP池。

---

## 文件清单

```
MSintership/
├── start_server.sh      # 启动脚本（已更新）
├── stop_server.sh       # 停止脚本（新增）
├── src/
│   ├── app.py           # 主应用
│   └── services/        # 服务模块
├── tests/
│   └── test_api.py      # 测试脚本
├── PROJECT_README.md    # 项目说明
├── TEST_REPORT.md       # 测试报告
└── FIXES.md             # 本文件
```

---

## 更新日志

**2026-01-14**
- ✅ 修复端口占用问题
- ✅ 添加停止服务脚本
- ✅ 更新启动脚本，添加端口检查
- ⚠️ 发现并记录证券完整查询的反爬虫问题
- 📝 创建问题修复说明文档

---

*如有其他问题，请查看服务日志或联系开发者*
