# 统一HTTP服务

集成证券从业人员查询和PDF下载代理功能的HTTP服务。

## 项目结构

```
MSintership/
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── app.py                    # 主Flask应用
│   ├── services/                 # 服务模块
│   │   ├── __init__.py
│   │   ├── sac_service.py        # 证券查询服务
│   │   └── pdf_service.py        # PDF下载服务
│   └── utils/                    # 工具模块
│       └── __init__.py
├── tests/                        # 测试目录
│   ├── test_api.py               # API测试脚本
│   └── output/                   # 测试输出目录
├── requirements.txt              # Python依赖
└── PROJECT_README.md             # 本文件
```

## 功能特性

### 1. 证券从业人员查询服务

- **搜索人员**: 通过姓名搜索证券从业人员
- **查询详情**: 通过UUID获取人员详细信息
- **完整查询**: 一次性获取所有匹配人员的完整信息

### 2. PDF下载代理服务

- 使用Selenium + Chrome浏览器下载PDF文件
- 可绕过常见的反爬虫措施
- 支持各种PDF下载场景

## 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装ChromeDriver (macOS)
brew install chromedriver

# 安装ChromeDriver (Linux)
sudo apt-get install chromium-chromedriver
```

## 启动服务

```bash
# 方式1: 直接运行
python src/app.py

# 方式2: 指定端口
PORT=8080 python src/app.py
```

默认端口: 5000

## API接口

### 健康检查

```bash
GET http://localhost:5000/health
```

### 证券查询API

#### 1. 搜索人员

```bash
# GET请求
GET http://localhost:5000/api/sac/search?name=张伟

# POST请求
POST http://localhost:5000/api/sac/search
Content-Type: application/json

{
  "name": "张伟"
}
```

#### 2. 查询详情

```bash
# GET请求
GET http://localhost:5000/api/sac/detail?uuid=<UUID>

# POST请求
POST http://localhost:5000/api/sac/detail
Content-Type: application/json

{
  "uuid": "<UUID>"
}
```

#### 3. 完整查询

```bash
# GET请求
GET http://localhost:5000/api/sac/full?name=张伟

# POST请求
POST http://localhost:5000/api/sac/full
Content-Type: application/json

{
  "name": "张伟"
}
```

### PDF下载API

```bash
# GET请求
GET http://localhost:5000/api/pdf/download?url=<PDF_URL>

# POST请求
POST http://localhost:5000/api/pdf/download
Content-Type: application/json

{
  "url": "<PDF_URL>"
}
```

## 运行测试

```bash
# 1. 先启动服务
python src/app.py

# 2. 在另一个终端运行测试
python tests/test_api.py
```

## 使用示例

### Python示例

```python
import requests

# 证券人员搜索
response = requests.post(
    'http://localhost:5000/api/sac/search',
    json={'name': '张伟'}
)
print(response.json())

# PDF下载
response = requests.post(
    'http://localhost:5000/api/pdf/download',
    json={'url': 'https://example.com/document.pdf'}
)
with open('downloaded.pdf', 'wb') as f:
    f.write(response.content)
```

### cURL示例

```bash
# 证券人员搜索
curl -X POST http://localhost:5000/api/sac/search \
  -H "Content-Type: application/json" \
  -d '{"name": "张伟"}'

# PDF下载
curl -X POST http://localhost:5000/api/pdf/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/document.pdf"}' \
  --output downloaded.pdf
```

## 注意事项

1. **Chrome浏览器**: 需要安装Chrome浏览器和ChromeDriver
2. **请求频率**: 证券查询API内置了延迟控制，避免请求过快
3. **超时设置**: PDF下载默认超时时间为120秒
4. **资源清理**: 服务会自动清理临时文件和浏览器实例

## 技术栈

- **Web框架**: Flask
- **浏览器自动化**: Selenium + ChromeDriver
- **HTTP客户端**: requests
- **日志**: Python logging

## 开发说明

### 添加新功能

1. 在 `src/services/` 中创建新的服务模块
2. 在 `src/app.py` 中添加新的API端点
3. 更新 `tests/test_api.py` 添加测试用例

### 日志配置

日志级别可以通过环境变量配置:

```bash
export LOG_LEVEL=DEBUG
python src/app.py
```

## 许可证

MIT License
