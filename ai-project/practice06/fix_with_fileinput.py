import fileinput
import sys

# 设置文件路径
file_path = r"D:\ttll\practice06\tool_client.py"

# 使用fileinput模块直接修改文件
with fileinput.FileInput(file_path, inplace=True, backup='.bak', encoding='utf-8') as file:
    for line in file:
        # 修复工具执行结果的输出
        if 'print(f"工具执行结果: {json.dumps(result, ensure_ascii=False)}")' in line:
            print('        print("工具执行结果:")')
            print('        import pprint')
            print('        pprint.pprint(result, indent=2, width=120)')
        elif 'print(f"工具执行结果: {json.dumps(tool_result, ensure_ascii=False)}")' in line:
            print('        print("工具执行结果:")')
            print('        import pprint')
            print('        pprint.pprint(tool_result, indent=2, width=120)')
        elif '"content": f"工具执行结果：{json.dumps(tool_result, ensure_ascii=False)}"' in line:
            print('                    "content": "工具执行结果：" + str(tool_result)')
        elif 'history.append({"role": "user", "content": f"工具执行结果: {json.dumps(' in line:
            # 修复历史记录中的工具执行结果
            line = line.replace('f"工具执行结果: {json.dumps(', '"工具执行结果: " + str(')
            line = line.replace(', ensure_ascii=False)}"', ')')
            print(line, end='')
        else:
            print(line, end='')

print("修复完成！")