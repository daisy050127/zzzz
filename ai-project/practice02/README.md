# 工具调用功能实现

本项目实现了一个基于LLM的工具调用系统，支持以下6个工具：

1. `list_files(directory)` - 列出某个目录下的所有文件和文件夹
2. `rename_file(directory, old_name, new_name)` - 修改某个目录下某个文件的名字
3. `delete_file(directory, filename)` - 删除某个目录下的某个文件
4. `create_file(directory, filename, content)` - 在某个目录下新建1个文件，并且写入内容
5. `read_file(directory, filename)` - 读取某个目录下的某个文件内容
6. `curl(url)` - 通过curl访问网页并返回网页内容

## 环境设置

1. 确保在项目根目录创建了 `.env` 文件，包含以下配置：

```
API_KEY=your_api_key
BASE_URL=https://api.openai.com/v1
MODEL=gpt-3.5-turbo
TIMEOUT=30
```

## 运行方式

### 1. 测试工具函数

```bash
# 测试原始工具客户端
python test_tool_client.py

# 测试新的工具聊天客户端
python test_tool_chat_client.py
```

### 2. 运行工具调用系统

```bash
# 运行原始工具客户端
python tool_client.py

# 运行新的工具聊天客户端
python tool_chat_client.py
```

然后输入您的请求，例如：
- "列出 practice02 目录下的文件"
- "在 practice02 目录下创建一个名为 test.txt 的文件，内容为 'Hello World'"
- "读取 practice02 目录下的 test.txt 文件内容"
- "将 practice02 目录下的 test.txt 文件重命名为 new_test.txt"
- "删除 practice02 目录下的 new_test.txt 文件"
- "访问 https://www.example.com 并返回网页内容"

## 工作原理

1. 系统将用户请求发送给LLM，并附带工具列表作为系统提示词
2. LLM分析请求，生成工具调用请求（如果需要）
3. 系统执行工具调用，获取结果
4. 系统将工具执行结果发送回LLM
5. LLM根据工具执行结果生成最终回复

## 示例输出

### 示例1：列出目录文件

```
请输入您的请求（例如：列出 practice02 目录下的文件）：
输入: 列出 practice02 目录下的文件

发送请求到 LLM API...
模型: gpt-3.5-turbo
基础 URL: https://api.openai.com/v1
提示: 列出 practice02 目录下的文件
================================================================================
工具执行结果:
- 工具: list_files
  结果: {"status": "success", "files": ["test_tool_client.py", "tool_client.py", "README.md"]}
================================================================================
最终回复内容:
practice02 目录下的文件有：
- test_tool_client.py
- tool_client.py
- README.md
================================================================================
统计信息:
总 Token 数: 120
耗时: 1.50 秒
```

### 示例2：访问网页

```
请输入您的请求（例如：列出 practice02 目录下的文件）：
输入: 访问 https://www.example.com 并返回网页内容

发送请求到 LLM API...
模型: gpt-3.5-turbo
基础 URL: https://api.openai.com/v1
提示: 访问 https://www.example.com 并返回网页内容
================================================================================
工具执行结果:
- 工具: curl
  结果: {"status": "success", "content": "<!doctype html><html lang=\"en\"><head><title>Example Domain</title>...</head><body><div><h1>Example Domain</h1><p>This domain is for use in documentation examples without needing permission. Avoid use in operations.</p><p><a href=\"https://iana.org/domains/example\">Learn more</a></p></div></body></html>"}
================================================================================
最终回复内容:
我已成功访问了 https://www.example.com 网页，内容如下：

```html
<!doctype html>
<html lang="en">
<head>
    <title>Example Domain</title>
    ...
</head>
<body>
    <div>
        <h1>Example Domain</h1>
        <p>This domain is for use in documentation examples without needing permission. Avoid use in operations.</p>
        <p><a href="https://iana.org/domains/example">Learn more</a></p>
    </div>
</body>
</html>
```

这是一个示例域名网页，用于在文档示例中使用，无需权限。
================================================================================
统计信息:
总 Token 数: 250
耗时: 2.00 秒
```
