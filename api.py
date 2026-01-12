"""
证券从业人员信息查询API - 最终版本

接口1：通过姓名查询人员列表，返回所有结果字段
接口2：通过接口1的uuid，获取个人基本信息和登记变更记录

官网地址: https://gs.sac.net.cn/pages/registration/sac-publicity-report.html
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
from typing import Dict, List
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SACPersonAPI:
    """证券从业人员信息查询API"""

    def __init__(self, headless: bool = True, sleep_time: int = 2):
        """
        初始化API客户端

        Args:
            headless: 是否使用无头模式（不显示浏览器窗口）
            sleep_time: API请求之间的延迟时间（秒），建议2-3秒
        """
        self.base_url = "https://gs.sac.net.cn"
        self.driver = None
        self.headless = headless
        self.sleep_time = sleep_time
        self._init_driver()

    def _init_driver(self):
        """初始化Chrome浏览器"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')

        # 反爬虫检测优化
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # 设置User-Agent - 模拟真实浏览器
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        chrome_options.add_argument(f'user-agent={user_agent}')

        try:
            self.driver = webdriver.Chrome(options=chrome_options)

            # 隐藏webdriver特征
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ["zh-CN", "zh", "en"]
                    });
                '''
            })

            logger.info("✓ Chrome浏览器初始化成功")

        except Exception as e:
            logger.error(f"✗ Chrome浏览器初始化失败: {e}")
            logger.info("\n请确保已安装Chrome浏览器和ChromeDriver:")
            logger.info("  macOS: brew install chromedriver")
            logger.info("  Linux: sudo apt-get install chromium-chromedriver")
            raise

    def _ensure_session_ready(self):
        """确保会话已经准备好，通过反爬虫检测"""
        if not self.driver.current_url.startswith(self.base_url):
            logger.info("初始化会话，访问主页...")
            self.driver.get(f"{self.base_url}/pages/registration/sac-publicity-name.html")
            logger.info("等待反爬虫检测...")
            time.sleep(3)  # 等待JavaScript执行和cookie设置

    def get_person_list_by_name(self, name: str, person_type: int = 1) -> Dict:
        """
        接口1：通过姓名查询人员列表，返回所有结果字段

        Args:
            name: 人员姓名
            person_type: 人员类型，默认为1（支持多机构类别查询）

        Returns:
            查询结果字典，包含所有字段:
            {
                "success": true,
                "code": 20000,
                "message": "成功",
                "data": {
                    "data": [
                        {
                            "uuid": "人员唯一标识符",
                            "practnrNo": "从业编号",
                            "name": "姓名",
                            "certifNo": "证书编号",
                            "regDate": "注册日期",
                            "orgName": "机构名称",
                            "pracCtegName": "执业类别名称",
                            "edu": "学历",
                            "gender": "性别",
                            ... (所有其他字段)
                        }
                    ]
                }
            }
        """
        try:
            logger.info(f"\n[接口1] 查询姓名: {name}")

            # 确保会话已准备
            self._ensure_session_ready()

            # 执行AJAX请求 - 使用浏览器的fetch API
            logger.info("发送API请求...")
            script = f"""
            return new Promise((resolve, reject) => {{
                fetch('{self.base_url}/publicity/getPersonListByName', {{
                    method: 'POST',
                    headers: {{
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Origin': '{self.base_url}',
                        'Referer': '{self.base_url}/pages/registration/sac-publicity-name.html'
                    }},
                    body: 'name={name}&type={person_type}'
                }})
                .then(response => {{
                    if (!response.ok) {{
                        throw new Error('HTTP error ' + response.status);
                    }}
                    return response.json();
                }})
                .then(data => resolve(data))
                .catch(error => reject(error.toString()));
            }});
            """

            result = self.driver.execute_script(script)

            # 添加延迟，避免请求过快
            time.sleep(self.sleep_time)

            if result and isinstance(result, dict):
                if result.get('success'):
                    person_list = result.get('data', {}).get('data', [])
                    logger.info(f"✓ 查询成功，找到 {len(person_list)} 个匹配的人员")
                else:
                    logger.warning(f"✗ 查询失败: {result.get('message', '未知错误')}")
            else:
                logger.error(f"✗ 返回结果格式异常: {result}")

            return result

        except Exception as e:
            error_msg = f"请求失败: {str(e)}"
            logger.error(f"✗ {error_msg}")
            return {"error": error_msg}

    def get_person_detail(self, uuid: str) -> Dict:
        """
        接口2：通过uuid获取个人基本信息和登记变更记录

        Args:
            uuid: 人员唯一标识符（从接口1的返回结果中获取）

        Returns:
            人员详细信息字典:
            {
                "success": true,
                "code": 20000,
                "message": "成功",
                "data": {
                    "data": {
                        "uuid": "人员唯一标识符",
                        "name": "姓名",
                        "gender": "性别",
                        "edu": "学历",
                        "orgName": "机构名称",
                        "pracCtegName": "执业类别",
                        "pracAreaName": "执业区域",
                        "servBrnName": "服务营业部",
                        "compWeb": "公司网站",
                        "compCompltConsltTel": "投诉咨询电话",
                        "regHistory": "[登记变更记录JSON字符串]",
                        ... (所有其他字段)
                    }
                }
            }
        """
        try:
            logger.info(f"\n[接口2] 查询UUID: {uuid}")

            # 确保会话已准备
            self._ensure_session_ready()

            # 执行AJAX请求
            logger.info("发送API请求...")
            script = f"""
            return new Promise((resolve, reject) => {{
                fetch('{self.base_url}/publicity/getPersonDetail', {{
                    method: 'POST',
                    headers: {{
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Origin': '{self.base_url}',
                        'Referer': '{self.base_url}/pages/registration/sac-publicity-name.html'
                    }},
                    body: 'uuid={uuid}'
                }})
                .then(response => {{
                    if (!response.ok) {{
                        throw new Error('HTTP error ' + response.status);
                    }}
                    return response.json();
                }})
                .then(data => resolve(data))
                .catch(error => reject(error.toString()));
            }});
            """

            result = self.driver.execute_script(script)

            # 添加延迟，避免请求过快
            time.sleep(self.sleep_time)

            if result and isinstance(result, dict):
                if result.get('success'):
                    logger.info(f"✓ 查询成功")
                else:
                    logger.warning(f"✗ 查询失败: {result.get('message', '未知错误')}")
            else:
                logger.error(f"✗ 返回结果格式异常: {result}")

            return result

        except Exception as e:
            error_msg = f"请求失败: {str(e)}"
            logger.error(f"✗ {error_msg}")
            return {"error": error_msg}

    def query_person_full_info(self, name: str) -> Dict:
        """
        完整查询：先通过姓名查询列表，再获取每个人的详细信息

        Args:
            name: 人员姓名

        Returns:
            {
                "name": "查询的姓名",
                "persons": [
                    {
                        "basic": {...},      # 接口1返回的基本信息
                        "detail": {...}      # 接口2返回的详细信息
                    }
                ]
            }
        """
        logger.info(f"\n[完整查询] 姓名: {name}")

        # 第一步：查询姓名列表
        list_result = self.get_person_list_by_name(name)

        if "error" in list_result or not list_result.get('success'):
            return {
                "name": name,
                "error": list_result.get('error') or list_result.get('message'),
                "persons": []
            }

        person_list = list_result.get('data', {}).get('data', [])

        # 第二步：查询每个人的详细信息
        full_info_list = []
        for i, person in enumerate(person_list, 1):
            uuid = person.get('uuid')
            logger.info(f"\n查询第 {i}/{len(person_list)} 个人员的详情 (UUID: {uuid})")

            detail_result = self.get_person_detail(uuid)

            full_info_list.append({
                "basic": person,  # 接口1的基本信息
                "detail": detail_result.get('data', {}).get('data', {}) if detail_result.get('success') else None
            })

        return {
            "name": name,
            "total": len(full_info_list),
            "persons": full_info_list
        }

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("\n✓ 浏览器已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
