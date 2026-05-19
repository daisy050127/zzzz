import json

# 测试数据
test_data = {
    "status": "success",
    "data": "这是一段包含\"引号\"和\n换行的文本"
}

print("使用json.dumps输出（带转义）:")
print(json.dumps(test_data, ensure_ascii=False))
print()

print("使用str()输出（无转义）:")
print(str(test_data))
print()

print("修复说明:")
print("- 将 json.dumps(result, ensure_ascii=False) 替换为 str(result)")
print("- str()函数不会转义特殊字符")
print("- 这样输出会显示真实的引号和换行符")