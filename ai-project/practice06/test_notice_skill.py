import json
import sys
import os

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tool_client import list_available_skills, load_skill_content

def test_skill_functions():
    print("=== 测试技能函数 ===")
    
    # 测试list_available_skills
    print("1. 测试list_available_skills:")
    skills_result = list_available_skills()
    print(f"技能列表: {json.dumps(skills_result, ensure_ascii=False)}")
    
    # 测试load_skill_content
    print("\n2. 测试load_skill_content:")
    notice_result = load_skill_content("notice")
    print(f"notice技能内容: {json.dumps(notice_result, ensure_ascii=False)}")
    
    print("\n测试完成")

if __name__ == "__main__":
    test_skill_functions()