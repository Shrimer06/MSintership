"""
证券从业人员信息查询API测试工具 - 最终版本

测试接口：
1. 通过姓名查询人员列表（返回所有字段）
2. 通过UUID查询个人基本信息和登记变更记录
"""
import json
import argparse
from sac_api_final import SACPersonAPI


def test_interface1(name: str = "张武"):
    """
    测试接口1：通过姓名查询人员列表

    Args:
        name: 查询的姓名
    """
    print("=" * 80)
    print("测试接口1: 通过姓名查询人员列表（返回所有字段）")
    print("=" * 80)
    print(f"\n查询姓名: {name}\n")

    with SACPersonAPI(headless=True, sleep_time=2) as api:
        result = api.get_person_list_by_name(name)

        # 保存结果
        with open('test_interface1_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        if result.get('success'):
            print("✓ 查询成功!\n")

            person_list = result.get('data', {}).get('data', [])
            print(f"找到 {len(person_list)} 个匹配的人员:\n")

            for i, person in enumerate(person_list, 1):
                print(f"[{i}] {person.get('name')}")
                print(f"    UUID: {person.get('uuid')}")
                print(f"    机构: {person.get('orgName')}")
                print(f"    证书编号: {person.get('certifNo')}")
                print(f"    执业类别: {person.get('pracCtegName')}")
                print(f"    学历: {person.get('edu')}")
                print(f"    性别: {person.get('gender')}")
                print()

            print(f"完整结果已保存到: test_interface1_result.json")

            return result
        else:
            print(f"✗ 查询失败: {result.get('message') or result.get('error')}")
            return None


def test_interface2(uuid: str = None, name: str = "张武"):
    """
    测试接口2：通过UUID查询个人基本信息和登记变更记录

    Args:
        uuid: 人员UUID（如果不提供，会先通过姓名查询获取）
        name: 当uuid为空时，通过姓名查询获取第一个人的uuid
    """
    print("=" * 80)
    print("测试接口2: 获取个人基本信息和登记变更记录")
    print("=" * 80)

    with SACPersonAPI(headless=True, sleep_time=2) as api:
        # 如果没有提供UUID，先通过姓名查询获取
        if not uuid:
            print(f"\n未提供UUID，先通过姓名查询获取...")
            list_result = api.get_person_list_by_name(name)

            if not list_result.get('success'):
                print(f"✗ 姓名查询失败: {list_result.get('message') or list_result.get('error')}")
                return None

            person_list = list_result.get('data', {}).get('data', [])
            if not person_list:
                print(f"✗ 未找到姓名为 '{name}' 的人员")
                return None

            uuid = person_list[0].get('uuid')
            print(f"✓ 获取到UUID: {uuid}\n")

        print(f"查询UUID: {uuid}\n")

        result = api.get_person_detail(uuid)

        # 保存结果
        with open('test_interface2_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        if result.get('success'):
            print("✓ 查询成功!\n")

            person = result.get('data', {}).get('data', {})

            print("基本信息:")
            print(f"  姓名: {person.get('name')}")
            print(f"  性别: {person.get('gender')}")
            print(f"  学历: {person.get('edu')}")
            print(f"  机构: {person.get('orgName')}")
            print(f"  证书编号: {person.get('certifNo')}")
            print(f"  执业类别: {person.get('pracCtegName')}")
            print(f"  执业区域: {person.get('pracAreaName')}")
            print(f"  服务营业部: {person.get('servBrnName')}")
            print(f"  公司网站: {person.get('compWeb')}")
            print(f"  投诉电话: {person.get('compCompltConsltTel')}")

            print("\n登记变更记录:")
            reg_history_str = person.get('regHistory')
            if reg_history_str:
                try:
                    history = json.loads(reg_history_str)
                    print(f"  共 {len(history)} 条记录:\n")
                    for i, record in enumerate(history, 1):
                        print(f"  [{i}] {record.get('status')}")
                        print(f"      证书编号: {record.get('certif_no')}")
                        print(f"      获得日期: {record.get('get_date')}")
                        print(f"      离开日期: {record.get('leave_date')}")
                        print(f"      机构: {record.get('org_name')}")
                        print(f"      类型: {record.get('reg_type')}")
                        print()
                except Exception as e:
                    print(f"  解析失败: {e}")
                    print(f"  原始数据: {reg_history_str}")
            else:
                print("  无登记变更记录")

            print(f"\n完整结果已保存到: test_interface2_result.json")

            return result
        else:
            print(f"✗ 查询失败: {result.get('message') or result.get('error')}")
            return None


def test_both_interfaces(name: str = "张武"):
    """
    测试完整流程：先查询列表，再查询每个人的详细信息

    Args:
        name: 查询的姓名
    """
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 22 + "证券从业人员信息查询API测试" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    with SACPersonAPI(headless=True, sleep_time=2) as api:
        # 第一步：测试接口1
        print("=" * 80)
        print("步骤1: 通过姓名查询人员列表")
        print("=" * 80)
        print(f"\n查询姓名: {name}\n")

        result1 = api.get_person_list_by_name(name)

        if not result1.get('success'):
            print(f"✗ 查询失败: {result1.get('message') or result1.get('error')}")
            return

        print("✓ 查询成功!\n")

        person_list = result1.get('data', {}).get('data', [])
        print(f"找到 {len(person_list)} 个匹配的人员:\n")

        all_results = {
            "name": name,
            "list_result": result1,
            "detail_results": []
        }

        # 第二步：测试接口2 - 查询每个人的详情
        for i, person in enumerate(person_list, 1):
            print(f"\n{'=' * 80}")
            print(f"步骤2.{i}: 查询第 {i} 个人员的详细信息")
            print("=" * 80)

            print(f"\n姓名: {person.get('name')}")
            print(f"UUID: {person.get('uuid')}")
            print(f"机构: {person.get('orgName')}\n")

            uuid = person.get('uuid')
            result2 = api.get_person_detail(uuid)

            if result2.get('success'):
                print("✓ 查询成功!")

                detail = result2.get('data', {}).get('data', {})

                print("\n基本信息:")
                print(f"  执业区域: {detail.get('pracAreaName')}")
                print(f"  服务营业部: {detail.get('servBrnName')}")
                print(f"  投诉电话: {detail.get('compCompltConsltTel')}")

                print("\n登记变更记录:")
                reg_history_str = detail.get('regHistory')
                if reg_history_str:
                    try:
                        history = json.loads(reg_history_str)
                        print(f"  共 {len(history)} 条记录")
                    except:
                        print(f"  原始数据长度: {len(reg_history_str)} 字符")
                else:
                    print("  无记录")

                all_results["detail_results"].append({
                    "uuid": uuid,
                    "name": person.get('name'),
                    "result": result2
                })
            else:
                print(f"✗ 查询失败: {result2.get('message') or result2.get('error')}")

        # 保存所有结果
        output_file = f"test_results_{name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        print(f"\n{'=' * 80}")
        print("测试完成")
        print("=" * 80)
        print(f"\n所有结果已保存到: {output_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="证券从业人员信息查询API测试工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python3 test_sac_final.py                      # 运行完整测试
  python3 test_sac_final.py --test1 张武         # 测试接口1
  python3 test_sac_final.py --test2 --name 张武  # 测试接口2（自动获取UUID）
  python3 test_sac_final.py --test2 --uuid UUID  # 测试接口2（指定UUID）
        """
    )

    parser.add_argument("--test1", metavar="NAME", help="测试接口1：查询指定姓名")
    parser.add_argument("--test2", action="store_true", help="测试接口2：查询详细信息")
    parser.add_argument("--uuid", help="测试接口2时使用的UUID")
    parser.add_argument("--name", help="查询的姓名（默认：张武）", default="张武")

    args = parser.parse_args()

    # 根据参数执行不同的测试
    if args.test1:
        test_interface1(args.test1)
    elif args.test2:
        test_interface2(uuid=args.uuid, name=args.name)
    else:
        # 没有指定参数，运行完整测试
        test_both_interfaces(args.name)


if __name__ == "__main__":
    main()
