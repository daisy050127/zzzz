import json
import sys
import os

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tool_client import load_skill_content

def test_skill_integration():
    print("=== 测试技能调用集成 ===")
    
    # 模拟用户请求
    user_input = "请撰写关于五一节放假的通知"
    print(f"用户输入: {user_input}")
    
    # 模拟LLM生成工具调用请求
    tool_call_request = {
        "tool_call": {
            "name": "load_skill_content",
            "params": {
                "skill_name": "notice"
            }
        }
    }
    
    print("\n1. LLM生成工具调用请求:")
    print(json.dumps(tool_call_request, ensure_ascii=False, indent=2))
    
    # 执行工具调用
    print("\n2. 执行工具调用:")
    result = load_skill_content("notice")
    print(f"工具执行结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 模拟LLM根据工具执行结果生成响应
    print("\n3. LLM根据工具执行结果生成响应:")
    print("基于notice技能的内容，LLM应该生成符合规则的通知")
    print("例如: XX部通知\n\n关于五一节放假的通知\n\n全体员工：\n\n根据国家法定节假日安排，2026年五一国际劳动节放假安排如下：\n\n一、放假时间：2026年5月1日至5月5日，共5天。\n二、调班安排：4月26日（星期日）、5月10日（星期六）正常上班。\n\n请各部门妥善安排工作，确保放假期间的安全与稳定。\n\n祝大家节日快乐！\n\nXX部\n2026年4月27日")
    
    # 测试指定部门的情况
    print("\n4. 测试指定部门的情况:")
    user_input2 = "我是销售部的，请撰写关于五一节放假的通知"
    print(f"用户输入: {user_input2}")
    print("LLM应该生成以'销售部通知'开头的内容")
    print("例如: 销售部通知\n\n关于五一节放假的通知\n\n全体销售部员工：\n\n根据国家法定节假日安排，2026年五一国际劳动节放假安排如下：\n\n一、放假时间：2026年5月1日至5月5日，共5天。\n二、调班安排：4月26日（星期日）、5月10日（星期六）正常上班。\n\n请各位同事在放假前完成手头工作，确保客户服务不受影响。\n\n祝大家节日快乐！\n\n销售部\n2026年4月27日")
    
    print("\n测试完成")

if __name__ == "__main__":
    test_skill_integration()