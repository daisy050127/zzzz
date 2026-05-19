# 最简单的修复方法：直接读取并替换

# 设置文件路径
file_path = r"D:\ttll\practice06\tool_client.py"

# 读取原文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 简单的字符串替换
# 使用更简单的模式匹配
old_str = 'print(f"工具执行结果: {json.dumps(result, ensure_ascii=False)}")'
new_str = '''print("工具执行结果:")
        import pprint
        pprint.pprint(result, indent=2, width=120)'''

# 执行替换
count = 0
if old_str in content:
    content = content.replace(old_str, new_str)
    count += 1
    print(f"替换了 {count} 处")

# 写入修复后的文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("文件已保存。")