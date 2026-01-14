#!/usr/bin/env python3
"""
统一HTTP服务测试脚本
Test Script for Unified HTTP Service
"""

import requests
import json
import time
import os

# 服务器地址
BASE_URL = "http://localhost:8888"


def print_section(title):
    """打印分隔标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health():
    """测试健康检查"""
    print_section("测试 1: 健康检查")

    url = f"{BASE_URL}/health"
    print(f"请求: GET {url}")

    try:
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_sac_search():
    """测试证券人员搜索"""
    print_section("测试 2: 证券人员搜索")

    # 测试姓名
    test_name = "张伟"

    # 方式1: GET请求
    print(f"\n方式1: GET请求")
    url = f"{BASE_URL}/api/sac/search?name={test_name}"
    print(f"请求: GET {url}")

    try:
        response = requests.get(url, timeout=30)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                person_list = data.get('data', {}).get('data', [])
                print(f"✓ 查询成功，找到 {len(person_list)} 个匹配的人员")

                # 显示前3个结果
                for i, person in enumerate(person_list[:3], 1):
                    print(f"\n人员 {i}:")
                    print(f"  姓名: {person.get('name')}")
                    print(f"  UUID: {person.get('uuid')}")
                    print(f"  机构: {person.get('orgName')}")
                    print(f"  执业类别: {person.get('pracCtegName')}")

                # 返回第一个UUID用于详情查询
                if person_list:
                    return person_list[0].get('uuid')
            else:
                print(f"❌ 查询失败: {data.get('message')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ 错误: {e}")

    return None


def test_sac_detail(uuid):
    """测试证券人员详情查询"""
    print_section("测试 3: 证券人员详情查询")

    if not uuid:
        print("⚠️  跳过测试（没有UUID）")
        return

    # 方式2: POST请求
    print(f"\n方式2: POST请求")
    url = f"{BASE_URL}/api/sac/detail"
    print(f"请求: POST {url}")
    print(f"参数: {{'uuid': '{uuid}'}}")

    try:
        response = requests.post(
            url,
            json={"uuid": uuid},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                detail = data.get('data', {}).get('data', {})
                print(f"✓ 查询成功")
                print(f"\n详细信息:")
                print(f"  姓名: {detail.get('name')}")
                print(f"  性别: {detail.get('gender')}")
                print(f"  学历: {detail.get('edu')}")
                print(f"  机构: {detail.get('orgName')}")
                print(f"  执业类别: {detail.get('pracCtegName')}")
                print(f"  执业区域: {detail.get('pracAreaName')}")
            else:
                print(f"❌ 查询失败: {data.get('message')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ 错误: {e}")


def test_sac_full():
    """测试证券人员完整查询"""
    print_section("测试 4: 证券人员完整查询")

    test_name = "李明"

    url = f"{BASE_URL}/api/sac/full"
    print(f"请求: POST {url}")
    print(f"参数: {{'name': '{test_name}'}}")

    try:
        response = requests.post(
            url,
            json={"name": test_name},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            print(f"✓ 查询成功，共找到 {total} 个人员")

            # 显示第一个完整信息
            persons = data.get('persons', [])
            if persons:
                print(f"\n第一个人员的完整信息:")
                person = persons[0]
                basic = person.get('basic', {})
                detail = person.get('detail', {})

                print(f"  基本信息:")
                print(f"    姓名: {basic.get('name')}")
                print(f"    机构: {basic.get('orgName')}")

                if detail:
                    print(f"  详细信息:")
                    print(f"    性别: {detail.get('gender')}")
                    print(f"    学历: {detail.get('edu')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ 错误: {e}")


def test_pdf_download():
    """测试PDF下载"""
    print_section("测试 5: PDF下载")

    # 测试URL - 使用一个公开的PDF文件
    test_pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

    url = f"{BASE_URL}/api/pdf/download"
    print(f"请求: POST {url}")
    print(f"参数: {{'url': '{test_pdf_url}'}}")

    try:
        response = requests.post(
            url,
            json={"url": test_pdf_url},
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            content_length = len(response.content)

            print(f"✓ 下载成功")
            print(f"  Content-Type: {content_type}")
            print(f"  文件大小: {content_length} bytes")

            # 保存文件
            output_dir = "tests/output"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "test_downloaded.pdf")

            with open(output_file, 'wb') as f:
                f.write(response.content)

            print(f"  已保存到: {output_file}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  错误信息: {error_data.get('message', 'Unknown error')}")
            except:
                print(response.text)

    except Exception as e:
        print(f"❌ 错误: {e}")


def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("  统一HTTP服务 - 自动化测试")
    print("=" * 60)
    print(f"服务器地址: {BASE_URL}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 测试1: 健康检查
    health_ok = test_health()
    if not health_ok:
        print("\n❌ 服务器未运行或健康检查失败!")
        print("请先启动服务: python src/app.py")
        return

    time.sleep(1)

    # 测试2: 证券人员搜索
    uuid = test_sac_search()
    time.sleep(2)

    # 测试3: 证券人员详情
    if uuid:
        test_sac_detail(uuid)
        time.sleep(2)

    # 测试4: 证券人员完整查询
    test_sac_full()
    time.sleep(2)

    # 测试5: PDF下载
    test_pdf_download()

    # 测试完成
    print_section("测试完成")
    print(f"完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n所有测试已执行完毕！")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试已中断")
    except Exception as e:
        print(f"\n\n测试异常: {e}")
        import traceback
        traceback.print_exc()
