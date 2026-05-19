import json
import sys
import os

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tool_client import load_skill_content

def test_tool_call():
    print("=== 测试工具调用 ===")
    
    # 模拟LLM工具调用请求
    tool_call_request = {
        "tool_call": {
            "name": "load_skill_content",
            "params": {
                "skill_name": "notice"
            }
        }
    }
    
    print("1. 模拟LLM工具调用请求:")
    print(json.dumps(tool_call_request, ensure_ascii=False, indent=2))
    
    # 执行工具调用
    print("\n2. 执行工具调用:")
    result = load_skill_content("notice")
    print(f"工具执行结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 模拟LLM根据工具执行结果生成响应
    print("\n3. 模拟LLM根据工具执行结果生成响应:")
    print("基于notice技能的内容，LLM应该生成符合规则的通知")
    print("例如: 当用户不说部门时，生成'XX部通知'开头的内容")
    print("当用户说自己是销售部时，生成'销售部通知'开头的内容")
    
    print("\n测试完成")

if __name__ == "__main__":
    test_tool_call()