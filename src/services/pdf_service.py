"""
PDF下载代理服务
PDF Download Proxy Service - 基于 Selenium + Chrome WebDriver
使用真实的 Chrome 浏览器下载 PDF 文件，可以绕过各种反爬措施
"""

import os
import time
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging

logger = logging.getLogger(__name__)

# 配置
DOWNLOAD_TIMEOUT = 120  # 下载超时时间（秒）
CHROME_HEADLESS = True  # 是否无头模式


def create_chrome_driver(download_dir: str) -> webdriver.Chrome:
    """
    创建 Chrome WebDriver 实例

    Args:
        download_dir: 下载文件保存目录

    Returns:
        webdriver.Chrome: Chrome 驱动实例
    """
    chrome_options = Options()

    # 无头模式
    if CHROME_HEADLESS:
        chrome_options.add_argument('--headless=new')

    # 基本配置
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    # 忽略 SSL 证书错误
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--allow-running-insecure-content')

    # 禁用自动化检测
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 设置下载行为
    prefs = {
        'download.default_directory': download_dir,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': False,
        'plugins.always_open_pdf_externally': True,  # 直接下载 PDF 而不是预览
    }
    chrome_options.add_experimental_option('prefs', prefs)

    # 尝试查找 ChromeDriver
    chromedriver_path = None

    # 尝试使用 webdriver-manager
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        wdm_path = ChromeDriverManager().install()
        # webdriver-manager 有时返回错误的路径，需要修正
        import os as wdm_os
        if wdm_os.path.basename(wdm_path) != 'chromedriver':
            # 查找同目录下的 chromedriver
            dir_path = wdm_os.path.dirname(wdm_path)
            chromedriver_candidate = wdm_os.path.join(dir_path, 'chromedriver')
            if wdm_os.path.exists(chromedriver_candidate):
                chromedriver_path = chromedriver_candidate
            else:
                # 尝试父目录
                parent_dir = wdm_os.path.dirname(dir_path)
                chromedriver_candidate = wdm_os.path.join(parent_dir, 'chromedriver')
                if wdm_os.path.exists(chromedriver_candidate):
                    chromedriver_path = chromedriver_candidate
        else:
            chromedriver_path = wdm_path
    except Exception as e:
        logger.warning(f"webdriver-manager 失败: {e}")

    if chromedriver_path:
        logger.info(f"使用 ChromeDriver: {chromedriver_path}")
        service = Service(chromedriver_path)
    else:
        # 回退到系统 PATH
        logger.info("使用系统 PATH 中的 chromedriver")
        service = Service()

    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 设置 CDP 命令允许下载
    driver.execute_cdp_cmd('Page.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': download_dir
    })

    return driver


def wait_for_download(download_dir: str, timeout: int = DOWNLOAD_TIMEOUT) -> str:
    """
    等待下载完成

    Args:
        download_dir: 下载目录
        timeout: 超时时间（秒）

    Returns:
        str: 下载完成的文件路径
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        files = os.listdir(download_dir)

        # 过滤掉临时文件
        completed_files = [
            f for f in files
            if not f.endswith('.crdownload')
            and not f.endswith('.tmp')
            and not f.startswith('.')
        ]

        if completed_files:
            file_path = os.path.join(download_dir, completed_files[0])
            # 确保文件写入完成
            time.sleep(0.5)
            return file_path

        time.sleep(0.5)

    raise TimeoutError(f"下载超时（{timeout}秒）")


def download_pdf_with_chrome(url: str) -> bytes:
    """
    使用 Chrome 浏览器下载 PDF

    Args:
        url: PDF 文件的 URL

    Returns:
        bytes: PDF 文件内容
    """
    # 创建临时下载目录
    download_dir = tempfile.mkdtemp(prefix='pdf_download_')
    driver = None

    try:
        logger.info(f"[Chrome] 创建 WebDriver，下载目录: {download_dir}")
        driver = create_chrome_driver(download_dir)

        logger.info(f"[Chrome] 导航到: {url}")
        driver.get(url)

        # 等待下载完成
        logger.info("[Chrome] 等待下载完成...")
        file_path = wait_for_download(download_dir)

        logger.info(f"[Chrome] 下载完成: {file_path}")

        # 读取文件内容
        with open(file_path, 'rb') as f:
            content = f.read()

        logger.info(f"[Chrome] 文件大小: {len(content)} bytes")
        return content

    finally:
        if driver:
            driver.quit()
        # 清理临时目录
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir, ignore_errors=True)
