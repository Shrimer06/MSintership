"""
HTTP API使用示例

演示如何在Python代码中调用证券从业人员信息查询HTTP API
"""
import requests
import json


class SACPersonHTTPClient:
    """HTTP API客户端封装"""

    def __init__(self, base_url: str = "http://localhost:5001"):
        """
        初始化客户端

        Args:
            base_url: API服务的基础URL
        """
        self.base_url = base_url

    def health_check(self) -> dict:
        """健康检查"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def get_person_list(self, name: str, person_type: int = 1) -> dict:
        """
        通过姓名查询人员列表

        Args:
            name: 人员姓名
            person_type: 人员类型，默认为1

        Returns:
            查询结果字典
        """
        response = requests.post(
            f"{self.base_url}/api/person/list",
            json={"name": name, "person_type": person_type}
        )
        return response.json()

    def get_person_detail(self, uuid: str) -> dict:
        """
        通过UUID查询个人详细信息

        Args:
            uuid: 人员UUID

        Returns:
            详细信息字典
        """
        response = requests.post(
            f"{self.base_url}/api/person/detail",
            json={"uuid": uuid}
        )
        return response.json()

    def get_person_full_info(self, name: str) -> dict:
        """
        完整查询（姓名→列表→详情）

        Args:
            name: 人员姓名

        Returns:
            完整信息字典
        """
        response = requests.post(
            f"{self.base_url}/api/person/full",
            json={"name": name}
        )
        return response.json()

    def reset_browser(self) -> dict:
        """重置浏览器实例"""
        response = requests.post(f"{self.base_url}/api/reset")
        return response.json()


def example_1_basic_query():
    """示例1：基本查询流程"""
    print("\n" + "=" * 80)
    print("示例1：基本查询流程")
    print("=" * 80)

    # 创建客户端
    client = SACPersonHTTPClient()

    # 1. 健康检查
    print("\n1. 健康检查...")
    health = client.health_check()
    print(f"   状态: {health.get('status')}")

    # 2. 查询人员列表
    print("\n2. 查询姓名为'张三'的人员...")
    list_result = client.get_person_list("张三")

    if list_result.get('success'):
        data = list_result.get('data', {})
        person_list = data.get('data', {}).get('data', [])
        print(f"   找到 {len(person_list)} 个匹配的人员")

        if person_list:
            # 3. 查询第一个人的详细信息
            first_person = person_list[0]
            uuid = first_person.get('uuid')
            name = first_person.get('name')

            print(f"\n3. 查询 {name} 的详细信息...")
            detail_result = client.get_person_detail(uuid)

            if detail_result.get('success'):
                detail = detail_result.get('data', {}).get('data', {}).get('data', {})
                print(f"   机构: {detail.get('orgName')}")
                print(f"   证书编号: {detail.get('certifNo')}")
                print(f"   执业类别: {detail.get('pracCtegName')}")
                print(f"   执业区域: {detail.get('pracAreaName')}")
            else:
                print(f"   查询失败: {detail_result.get('error')}")
    else:
        print(f"   查询失败: {list_result.get('error')}")


def example_2_full_query():
    """示例2：使用完整查询接口"""
    print("\n" + "=" * 80)
    print("示例2：使用完整查询接口")
    print("=" * 80)

    client = SACPersonHTTPClient()

    print("\n查询姓名为'刘洋'的所有人员信息...")
    result = client.get_person_full_info("刘洋")

    if result.get('success'):
        data = result.get('data', {})
        name = data.get('name')
        total = data.get('total', 0)
        persons = data.get('persons', [])

        print(f"\n找到 {total} 个名叫'{name}'的人员:")

        for i, person in enumerate(persons, 1):
            basic = person.get('basic', {})
            detail = person.get('detail', {})

            print(f"\n[{i}] {basic.get('name')}")
            print(f"    机构: {basic.get('orgName')}")
            print(f"    证书编号: {basic.get('certifNo')}")
            print(f"    执业类别: {basic.get('pracCtegName')}")

            if detail:
                print(f"    执业区域: {detail.get('pracAreaName')}")
                print(f"    服务营业部: {detail.get('servBrnName')}")

                # 解析登记变更记录
                reg_history_str = detail.get('regHistory')
                if reg_history_str:
                    try:
                        history = json.loads(reg_history_str)
                        print(f"    登记变更记录: {len(history)} 条")
                    except:
                        pass
    else:
        print(f"查询失败: {result.get('error')}")


def example_3_error_handling():
    """示例3：错误处理"""
    print("\n" + "=" * 80)
    print("示例3：错误处理")
    print("=" * 80)

    client = SACPersonHTTPClient()

    # 1. 缺少参数
    print("\n1. 测试缺少参数的情况...")
    try:
        response = requests.post(
            "http://localhost:5000/api/person/list",
            json={}
        )
        result = response.json()
        print(f"   响应: {result}")
    except Exception as e:
        print(f"   异常: {e}")

    # 2. 查询不存在的UUID
    print("\n2. 测试查询不存在的UUID...")
    result = client.get_person_detail("invalid-uuid-12345")
    print(f"   成功: {result.get('success')}")
    if not result.get('success'):
        print(f"   错误: {result.get('error')}")

    # 3. 服务不可用
    print("\n3. 测试连接到不可用的服务...")
    try:
        bad_client = SACPersonHTTPClient("http://localhost:9999")
        bad_client.health_check()
    except requests.exceptions.ConnectionError:
        print("   无法连接到服务（预期行为）")


def example_4_batch_query():
    """示例4：批量查询"""
    print("\n" + "=" * 80)
    print("示例4：批量查询多个姓名")
    print("=" * 80)

    client = SACPersonHTTPClient()
    names = ["张三", "李四", "王五"]

    for name in names:
        print(f"\n查询: {name}")
        result = client.get_person_list(name)

        if result.get('success'):
            data = result.get('data', {})
            person_list = data.get('data', {}).get('data', [])
            print(f"  找到 {len(person_list)} 个匹配的人员")

            # 显示前3个
            for i, person in enumerate(person_list[:3], 1):
                print(f"    [{i}] {person.get('name')} - {person.get('orgName')}")

            if len(person_list) > 3:
                print(f"    ... 还有 {len(person_list) - 3} 个")
        else:
            print(f"  查询失败: {result.get('error')}")


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 22 + "HTTP API 使用示例" + " " * 23 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        # 运行示例
        example_1_basic_query()
        example_2_full_query()
        example_3_error_handling()
        example_4_batch_query()

        print("\n" + "=" * 80)
        print("所有示例运行完成")
        print("=" * 80)

    except requests.exceptions.ConnectionError:
        print("\n✗ 无法连接到HTTP API服务")
        print("  请确保服务已启动: python3 http_api.py")


if __name__ == "__main__":
    main()
