import json

# 测试json.dumps的输出
test_data = {
    "status": "success",
    "data": "这是一段包含\"引号\"和\n换行的文本"
}

print("使用json.dumps输出（带转义）:")
print(json.dumps(test_data, ensure_ascii=False))
print()

print("使用json.dumps输出（带缩进，仍有转义）:")
print(json.dumps(test_data, ensure_ascii=False, indent=2))
print()

print("直接输出数据内容（无转义）:")
print(f"status: {test_data['status']}")
print(f"data: {test_data['data']}")
print()

print("结论：json.dumps会自动转义特殊字符，这是JSON格式的特性。")
print("如果想要无转义输出，可以直接打印数据内容，而不是使用json.dumps。")