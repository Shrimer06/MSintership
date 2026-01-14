#!/usr/bin/env python3
"""
统一HTTP服务 - 集成证券查询和PDF下载功能
Unified HTTP Service - Securities Query & PDF Download
"""

import os
import sys
import time
import logging
from flask import Flask, request, jsonify, Response
from urllib.parse import urlparse, unquote

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.sac_service import SACPersonAPI
from services.pdf_service import download_pdf_with_chrome

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# 全局SAC API客户端（避免频繁创建和关闭浏览器）
sac_client = None


def get_sac_client():
    """获取SAC API客户端实例（单例模式）"""
    global sac_client
    if sac_client is None:
        logger.info("初始化SAC API客户端...")
        sac_client = SACPersonAPI(headless=True, sleep_time=2)
    return sac_client


# ==================== 健康检查 ====================

@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'message': '统一HTTP服务运行中',
        'services': {
            'sac_query': {
                'name': '证券从业人员查询',
                'endpoints': [
                    '/api/sac/search',
                    '/api/sac/detail',
                    '/api/sac/full'
                ]
            },
            'pdf_download': {
                'name': 'PDF下载代理',
                'endpoints': [
                    '/api/pdf/download'
                ]
            }
        },
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })


# ==================== 证券查询API ====================

@app.route('/api/sac/search', methods=['GET', 'POST'])
def sac_search():
    """
    证券从业人员查询 - 按姓名搜索

    GET:  /api/sac/search?name=<姓名>
    POST: /api/sac/search with JSON {"name": "<姓名>"}
    """
    try:
        # 获取参数
        if request.method == 'GET':
            name = request.args.get('name')
        else:
            data = request.get_json() or {}
            name = data.get('name')

        if not name:
            return jsonify({
                'success': False,
                'error': '缺少参数: name',
                'usage': {
                    'GET': '/api/sac/search?name=<姓名>',
                    'POST': '/api/sac/search with JSON {"name": "<姓名>"}'
                }
            }), 400

        logger.info(f"[SAC搜索] 姓名: {name}")

        # 调用服务
        client = get_sac_client()
        result = client.get_person_list_by_name(name)

        return jsonify(result)

    except Exception as e:
        logger.error(f"[SAC搜索] 错误: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '服务器内部错误',
            'message': str(e)
        }), 500


@app.route('/api/sac/detail', methods=['GET', 'POST'])
def sac_detail():
    """
    证券从业人员详情 - 按UUID查询

    GET:  /api/sac/detail?uuid=<UUID>
    POST: /api/sac/detail with JSON {"uuid": "<UUID>"}
    """
    try:
        # 获取参数
        if request.method == 'GET':
            uuid = request.args.get('uuid')
        else:
            data = request.get_json() or {}
            uuid = data.get('uuid')

        if not uuid:
            return jsonify({
                'success': False,
                'error': '缺少参数: uuid',
                'usage': {
                    'GET': '/api/sac/detail?uuid=<UUID>',
                    'POST': '/api/sac/detail with JSON {"uuid": "<UUID>"}'
                }
            }), 400

        logger.info(f"[SAC详情] UUID: {uuid}")

        # 调用服务
        client = get_sac_client()
        result = client.get_person_detail(uuid)

        return jsonify(result)

    except Exception as e:
        logger.error(f"[SAC详情] 错误: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '服务器内部错误',
            'message': str(e)
        }), 500


@app.route('/api/sac/full', methods=['GET', 'POST'])
def sac_full():
    """
    证券从业人员完整信息 - 按姓名查询所有详情

    GET:  /api/sac/full?name=<姓名>
    POST: /api/sac/full with JSON {"name": "<姓名>"}
    """
    try:
        # 获取参数
        if request.method == 'GET':
            name = request.args.get('name')
        else:
            data = request.get_json() or {}
            name = data.get('name')

        if not name:
            return jsonify({
                'success': False,
                'error': '缺少参数: name',
                'usage': {
                    'GET': '/api/sac/full?name=<姓名>',
                    'POST': '/api/sac/full with JSON {"name": "<姓名>"}'
                }
            }), 400

        logger.info(f"[SAC完整查询] 姓名: {name}")

        # 调用服务
        client = get_sac_client()
        result = client.query_person_full_info(name)

        return jsonify(result)

    except Exception as e:
        logger.error(f"[SAC完整查询] 错误: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '服务器内部错误',
            'message': str(e)
        }), 500


# ==================== PDF下载API ====================

@app.route('/api/pdf/download', methods=['GET', 'POST'])
def pdf_download():
    """
    PDF下载代理

    GET:  /api/pdf/download?url=<PDF_URL>
    POST: /api/pdf/download with JSON {"url": "<PDF_URL>"}
    """
    try:
        # 获取参数
        if request.method == 'GET':
            url = request.args.get('url')
        else:
            data = request.get_json() or {}
            url = data.get('url')

        if not url:
            return jsonify({
                'success': False,
                'error': '缺少参数: url',
                'usage': {
                    'GET': '/api/pdf/download?url=<PDF_URL>',
                    'POST': '/api/pdf/download with JSON {"url": "<PDF_URL>"}'
                }
            }), 400

        logger.info(f"[PDF下载] URL: {url}")

        # 调用服务
        pdf_content = download_pdf_with_chrome(url)

        # 从 URL 提取文件名
        parsed = urlparse(url)
        filename = os.path.basename(unquote(parsed.path)) or 'download.pdf'
        if not filename.endswith('.pdf'):
            filename += '.pdf'

        logger.info(f"[PDF下载] 成功: {filename}, {len(pdf_content)} bytes")

        return Response(
            pdf_content,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': len(pdf_content)
            }
        )

    except Exception as e:
        logger.error(f"[PDF下载] 错误: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'PDF下载失败',
            'message': str(e)
        }), 500


# ==================== 应用启动 ====================

def cleanup():
    """清理资源"""
    global sac_client
    if sac_client:
        logger.info("关闭SAC API客户端...")
        sac_client.close()
        sac_client = None


if __name__ == '__main__':
    import atexit

    # 注册退出清理
    atexit.register(cleanup)

    # 启动服务
    port = int(os.environ.get('PORT', 5000))

    print("=" * 60)
    print("统一HTTP服务已启动")
    print("=" * 60)
    print(f"服务地址: http://localhost:{port}")
    print(f"健康检查: http://localhost:{port}/health")
    print()
    print("证券查询API:")
    print(f"  - 搜索人员: http://localhost:{port}/api/sac/search?name=<姓名>")
    print(f"  - 查询详情: http://localhost:{port}/api/sac/detail?uuid=<UUID>")
    print(f"  - 完整查询: http://localhost:{port}/api/sac/full?name=<姓名>")
    print()
    print("PDF下载API:")
    print(f"  - 下载PDF:  http://localhost:{port}/api/pdf/download?url=<PDF_URL>")
    print("=" * 60)

    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n正在关闭服务...")
        cleanup()
