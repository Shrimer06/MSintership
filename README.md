# 证券从业人员信息查询API

简洁、高效的证券从业人员信息查询工具，基于Selenium实现，成功绕过反爬虫检测。

**官网**: https://gs.sac.net.cn/pages/registration/sac-publicity-report.html

---

## 快速开始

### 1. 安装依赖

```bash
pip3 install selenium
brew install chromedriver  # macOS
```

### 2. 运行测试

```bash
python3 test_sac_final.py
```

### 3. 在代码中使用

```python
from sac_api_final import SACPersonAPI

with SACPersonAPI(headless=True, sleep_time=2) as api:
    # 接口1：通过姓名查询人员列表
    result = api.get_person_list_by_name("张武")

    if result.get('success'):
        person_list = result['data']['data']

        # 接口2：获取个人详细信息
        uuid = person_list[0]['uuid']
        detail = api.get_person_detail(uuid)
```

---

## 核心接口

### 接口1：get_person_list_by_name(name)

通过姓名查询人员列表，返回所有字段。

**参数**:
- `name` (str): 人员姓名

**返回示例**:
```json
{
  "success": true,
  "code": 20000,
  "message": "成功",
  "data": {
    "data": [
      {
        "uuid": "1614059641131062377",
        "name": "张武",
        "certifNo": "L0740123050008",
        "orgName": "西部证券投资(西安)有限公司",
        "pracCtegName": "一般证券业务",
        "edu": "硕士研究生",
        "gender": "男",
        "regDate": "2023-05-09",
        "practnrNo": "017816"
      }
    ]
  }
}
```

### 接口2：get_person_detail(uuid)

通过UUID获取个人基本信息和登记变更记录。

**参数**:
- `uuid` (str): 人员唯一标识符（从接口1获取）

**返回示例**:
```json
{
  "success": true,
  "code": 20000,
  "message": "成功",
  "data": {
    "data": {
      "uuid": "1614059641131062377",
      "name": "张武",
      "orgName": "西部证券投资(西安)有限公司",
      "pracAreaName": null,
      "servBrnName": null,
      "compWeb": "https://oa.xbzqtzoa.com/",
      "compCompltConsltTel": "029-87211126",
      "regHistory": "[{\"certif_no\":\"S0800100010109\",\"status\":\"离职注销\",...}]"
    }
  }
}
```

**登记变更记录解析**:
```python
import json
person = detail['data']['data']
history = json.loads(person['regHistory'])

for record in history:
    print(f"{record['status']}: {record['org_name']}")
    print(f"  证书编号: {record['certif_no']}")
    print(f"  获得日期: {record['get_date']}")
    print(f"  离开日期: {record['leave_date']}")
```

---

## 使用示例

### 示例1：查询单个姓名

```python
from sac_api_final import SACPersonAPI

with SACPersonAPI(headless=True) as api:
    result = api.get_person_list_by_name("张武")

    if result.get('success'):
        for person in result['data']['data']:
            print(f"{person['name']} - {person['orgName']}")
```

### 示例2：查询完整信息

```python
from sac_api_final import SACPersonAPI
import json

with SACPersonAPI(headless=True) as api:
    # 先查询姓名列表
    result = api.get_person_list_by_name("张武")

    if result.get('success'):
        # 查询每个人的详细信息
        for person in result['data']['data']:
            uuid = person['uuid']
            detail = api.get_person_detail(uuid)

            if detail.get('success'):
                person_detail = detail['data']['data']

                # 基本信息
                print(f"姓名: {person_detail['name']}")
                print(f"机构: {person_detail['orgName']}")
                print(f"电话: {person_detail['compCompltConsltTel']}")

                # 登记变更记录
                history = json.loads(person_detail['regHistory'])
                print(f"登记记录: {len(history)} 条")
```

### 示例3：批量查询

```python
from sac_api_final import SACPersonAPI

with SACPersonAPI(headless=True, sleep_time=2) as api:
    names = ["张武", "王芳", "李明"]

    for name in names:
        result = api.get_person_list_by_name(name)
        if result.get('success'):
            count = len(result['data']['data'])
            print(f"{name}: 找到 {count} 个人员")
```

---

## 命令行工具

### 测试完整流程

```bash
python3 test_sac_final.py
```

### 测试接口1

```bash
python3 test_sac_final.py --test1 张武
```

### 测试接口2

```bash
python3 test_sac_final.py --test2 --name 张武
```

### 指定UUID查询

```bash
python3 test_sac_final.py --test2 --uuid 1614059641131062377
```

---

## API参数说明

### SACPersonAPI构造函数

```python
SACPersonAPI(
    headless=True,    # 是否使用无头模式（不显示浏览器窗口）
    sleep_time=2      # API请求间隔时间（秒），建议2-3秒
)
```

**参数说明**:
- `headless` (bool): 无头模式，推荐使用True
- `sleep_time` (int): 请求间隔时间，避免被封IP，建议2-3秒

---

## 返回字段说明

### 接口1返回字段（人员列表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| uuid | string | 人员唯一标识符 |
| name | string | 姓名 |
| certifNo | string | 证书编号 |
| orgName | string | 机构名称 |
| pracCtegName | string | 执业类别 |
| edu | string | 学历 |
| gender | string | 性别 |
| regDate | string | 注册日期 |
| practnrNo | string | 从业编号 |
| staffNo | string | 员工编号 |
| orgId | string | 机构ID |
| regCnt | number | 登记数量 |

### 接口2返回字段（人员详情）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| uuid | string | 人员唯一标识符 |
| name | string | 姓名 |
| gender | string | 性别 |
| edu | string | 学历 |
| orgName | string | 机构名称 |
| pracCtegName | string | 执业类别 |
| pracAreaName | string | 执业区域 |
| servBrnName | string | 服务营业部 |
| compWeb | string | 公司网站 |
| compCompltConsltTel | string | 投诉咨询电话 |
| photoPath | string | 照片路径（Base64） |
| regHistory | string | 登记变更记录（JSON字符串） |

### 登记变更记录字段（regHistory解析后）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| certif_no | string | 证书编号 |
| status | string | 状态（正常/离职注销） |
| get_date | string | 获得日期 |
| leave_date | string | 离开日期 |
| org_name | string | 机构名称 |
| reg_type | string | 登记类型 |

---

## 技术说明

### 为什么需要Selenium？

网站启用了**腾讯EdgeOne反爬虫防护**，直接使用requests会返回JavaScript挑战脚本而不是真实数据。使用Selenium模拟真实浏览器可以成功绕过检测。

### 反爬虫对策

1. ✅ 使用Selenium模拟真实浏览器
2. ✅ 隐藏webdriver特征
3. ✅ 先访问主页获取cookies
4. ✅ 等待JavaScript执行（3秒）
5. ✅ 使用真实的User-Agent和请求头
6. ✅ 请求间隔2-3秒

### 请求头配置

```javascript
{
  'Accept': 'application/json, text/javascript, */*; q=0.01',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  'Content-Type': 'application/x-www-form-urlencoded',
  'X-Requested-With': 'XMLHttpRequest',
  'Origin': 'https://gs.sac.net.cn',
  'Referer': 'https://gs.sac.net.cn/pages/registration/sac-publicity-name.html'
}
```

---

## 性能数据

| 操作 | 耗时 |
|------|------|
| 初始化浏览器 | ~1秒 |
| 反爬虫检测 | 3秒 |
| 接口1查询 | ~2秒 |
| 接口2查询 | ~2秒 |
| **单次完整查询** | **~8-10秒** |

---

## 注意事项

### ⚠️ 重要提醒

1. **请求频率**: 建议间隔2-3秒，避免被封IP
2. **资源清理**: 使用`with`语句自动关闭浏览器
3. **版本匹配**: 确保ChromeDriver与Chrome浏览器版本一致
4. **合规使用**: 仅用于合法查询，遵守网站使用条款

### 常见问题

**Q: ChromeDriver版本不匹配怎么办？**
```bash
# macOS
brew reinstall chromedriver

# 检查Chrome版本
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
```

**Q: 查询失败怎么办？**
- 检查网络连接
- 增加`sleep_time`参数（如：`sleep_time=3`）
- 等待几分钟后重试

**Q: 如何避免被封IP？**
- 设置合理的请求间隔（2-3秒）
- 不要频繁大量请求
- 使用完毕及时关闭浏览器

---

## 错误处理

```python
from sac_api_final import SACPersonAPI

with SACPersonAPI(headless=True) as api:
    result = api.get_person_list_by_name("张武")

    # 检查错误
    if "error" in result:
        print(f"请求失败: {result['error']}")
    elif not result.get('success'):
        print(f"查询失败: {result.get('message')}")
    else:
        # 处理成功结果
        person_list = result['data']['data']
        print(f"找到 {len(person_list)} 个人员")
```

---

## 项目文件

```
MSintership/
├── sac_api_final.py      # API封装模块
├── test_sac_final.py     # 测试工具
└── README.md             # 项目文档
```

---

## 依赖说明

### 必需依赖
- `selenium` >= 4.0
- `chromedriver` (与Chrome浏览器版本匹配)

### 安装方法

**macOS**:
```bash
pip3 install selenium
brew install chromedriver
```

**Linux**:
```bash
pip3 install selenium
sudo apt-get install chromium-chromedriver
```

**Windows**:
```bash
pip3 install selenium
# 从 https://chromedriver.chromium.org/ 下载并配置环境变量
```

---

## 测试验证

✅ **接口1测试通过**
- 查询姓名"张武"
- 返回5个人员
- 所有字段完整

✅ **接口2测试通过**
- 查询UUID
- 返回基本信息
- 包含3条登记变更记录

---

## 参考资源

- **GitHub项目**: https://github.com/qzcool/SAC （参考项目）
- **官网地址**: https://gs.sac.net.cn
- **Selenium文档**: https://selenium-python.readthedocs.io/

---

## 许可证

MIT License

---

## 更新日志

### v1.0 (2026-01-12)
- ✅ 实现接口1：通过姓名查询人员列表
- ✅ 实现接口2：获取个人详细信息和登记变更记录
- ✅ 成功绕过腾讯EdgeOne反爬虫检测
- ✅ 完整的文档和示例代码
- ✅ 测试验证通过

---

**开发者**: 基于 [qzcool/SAC](https://github.com/qzcool/SAC) 项目优化
