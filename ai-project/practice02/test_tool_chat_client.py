import os
import json
from tool_chat_client import list_files, rename_file, delete_file, create_file, read_file, curl

# 测试目录
test_dir = os.path.dirname(os.path.abspath(__file__))

def test_list_files():
    print("测试 list_files 函数...")
    result = list_files(test_dir)
    print(f"结果: {json.dumps(result, ensure_ascii=False)}")
    assert result['status'] == 'success'
    print("OK: list_files 测试通过")

def test_create_file():
    print("\n测试 create_file 函数...")
    test_file = "test.txt"
    content = "这是一个测试文件"
    result = create_file(test_dir, test_file, content)
    print(f"结果: {json.dumps(result, ensure_ascii=False)}")
    assert result['status'] == 'success'
    assert os.path.exists(os.path.join(test_dir, test_file))
    print("OK: create_file 测试通过")

def test_read_file():
    print("\n测试 read_file 函数...")
    test_file = "test.txt"
    result = read_file(test_dir, test_file)
    print(f"结果: {json.dumps(result, ensure_ascii=False)}")
    assert result['status'] == 'success'
    assert result['content'] == "这是一个测试文件"
    print("OK: read_file 测试通过")

def test_rename_file():
    print("\n测试 rename_file 函数...")
    old_name = "test.txt"
    new_name = "renamed_test.txt"
    result = rename_file(test_dir, old_name, new_name)
    print(f"结果: {json.dumps(result, ensure_ascii=False)}")
    assert result['status'] == 'success'
    assert not os.path.exists(os.path.join(test_dir, old_name))
    assert os.path.exists(os.path.join(test_dir, new_name))
    print("OK: rename_file 测试通过")

def test_delete_file():
    print("\n测试 delete_file 函数...")
    test_file = "renamed_test.txt"
    result = delete_file(test_dir, test_file)
    print(f"结果: {json.dumps(result, ensure_ascii=False)}")
    assert result['status'] == 'success'
    assert not os.path.exists(os.path.join(test_dir, test_file))
    print("OK: delete_file 测试通过")

def test_curl():
    print("\n测试 curl 函数...")
    test_url = "https://www.example.com"
    result = curl(test_url)
    print(f"结果: {json.dumps(result, ensure_ascii=False)}")
    assert result['status'] == 'success'
    assert len(result['content']) > 0
    print("OK: curl 测试通过")

if __name__ == "__main__":
    print("开始测试工具函数...")
    print("测试目录:", test_dir)
    print("=" * 60)
    
    try:
        test_list_files()
        test_create_file()
        test_read_file()
        test_rename_file()
        test_delete_file()
        test_curl()
        print("\n" + "=" * 60)
        print("所有测试通过！")
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
