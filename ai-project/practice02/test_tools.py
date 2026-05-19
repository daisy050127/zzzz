import os
import json

# 导入工具函数
from tool_client import list_files, rename_file, delete_file, create_file, read_file

# 测试目录
TEST_DIR = './test_files'

# 确保测试目录存在
if not os.path.exists(TEST_DIR):
    os.makedirs(TEST_DIR)

print("=== 测试工具函数 ===")
print(f"测试目录: {TEST_DIR}")
print("====================")

# 测试1: 列出文件（初始状态）
print("\n1. 测试列出文件（初始状态）:")
result = list_files(TEST_DIR)
print(json.dumps(result, ensure_ascii=False, indent=2))

# 测试2: 创建文件
print("\n2. 测试创建文件:")
test_content = "这是一个测试文件\nHello, World!\n"
result = create_file(TEST_DIR, 'test.txt', test_content)
print(json.dumps(result, ensure_ascii=False, indent=2))

# 测试3: 再次列出文件
print("\n3. 测试再次列出文件:")
result = list_files(TEST_DIR)
print(json.dumps(result, ensure_ascii=False, indent=2))

# 测试4: 读取文件
print("\n4. 测试读取文件:")
result = read_file(TEST_DIR, 'test.txt')
print(json.dumps(result, ensure_ascii=False, indent=2))

# 测试5: 重命名文件
print("\n5. 测试重命名文件:")
result = rename_file(TEST_DIR, 'test.txt', 'renamed_test.txt')
print(json.dumps(result, ensure_ascii=False, indent=2))

# 测试6: 列出文件（重命名后）
print("\n6. 测试列出文件（重命名后）:")
result = list_files(TEST_DIR)
print(json.dumps(result, ensure_ascii=False, indent=2))

# 测试7: 删除文件
print("\n7. 测试删除文件:")
result = delete_file(TEST_DIR, 'renamed_test.txt')
print(json.dumps(result, ensure_ascii=False, indent=2))

# 测试8: 列出文件（删除后）
print("\n8. 测试列出文件（删除后）:")
result = list_files(TEST_DIR)
print(json.dumps(result, ensure_ascii=False, indent=2))

print("\n=== 测试完成 ===")

# 清理测试目录
if os.path.exists(TEST_DIR):
    import shutil
    shutil.rmtree(TEST_DIR)
    print(f"测试目录 {TEST_DIR} 已清理")
