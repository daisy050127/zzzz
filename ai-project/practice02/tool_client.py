import os
import time
import json
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse

# 读取 .env 文件
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"')
    return env_vars

# 计算字符串的 token 数量（简化版，实际应使用对应模型的 tokenizer）
def count_tokens(text):
    return len(text.split())

# 工具函数 1：列出某个目录下某个文件的名字
def list_files(directory):
    try:
        files = os.listdir(directory)
        return {"status": "success", "files": files}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数 2：修改某个目录下某个文件的名字
def rename_file(directory, old_name, new_name):
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)
        return {"status": "success", "message": f"文件已重命名为 {new_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数 3：删除某个目录下的某个文件
def delete_file(directory, filename):
    try:
        file_path = os.path.join(directory, filename)
        os.remove(file_path)
        return {"status": "success", "message": "文件已删除"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数 4：在某个目录下新建1个文件，并且写入内容
def create_file(directory, filename, content):
    try:
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": "文件已创建"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数 5：读取某个目录下的某个文件内容
def read_file(directory, filename):
    try:
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数 6：通过curl访问网页并返回网页内容
def curl(url):
    try:
        # 解析 URL
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        path = parsed_url.path or '/'
        if parsed_url.query:
            path += '?' + parsed_url.query
        
        # 根据 scheme 选择连接类型
        if parsed_url.scheme == 'https':
            conn = HTTPSConnection(host, timeout=30)
        else:
            conn = HTTPConnection(host, timeout=30)
        
        # 发送请求
        conn.request("GET", path)
        response = conn.getresponse()
        
        # 读取响应
        content = response.read().decode('utf-8', errors='ignore')
        conn.close()
        
        # 限制返回内容长度，避免token过多
        max_length = 2000
        if len(content) > max_length:
            content = content[:max_length] + "... (内容已截断)"
        
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 发送请求到 LLM API
def call_llm(prompt, env_vars):
    # 解析 BASE_URL
    url = urlparse(env_vars.get('BASE_URL', 'https://api.openai.com/v1'))
    host = url.netloc
    path = url.path or '/v1'
    if not path.endswith('/'):
        path += '/'
    path += 'chat/completions'
    
    # 构建请求数据
    data = {
        "model": env_vars.get('MODEL', 'gpt-3.5-turbo'),
        "messages": [
            {"role": "system", "content": "你是一个助手，能够使用以下工具来执行文件操作和网络访问：\n\n工具列表：\n1. list_files(directory) - 列出某个目录下的所有文件和文件夹\n2. rename_file(directory, old_name, new_name) - 修改某个目录下某个文件的名字\n3. delete_file(directory, filename) - 删除某个目录下的某个文件\n4. create_file(directory, filename, content) - 在某个目录下新建1个文件，并且写入内容\n5. read_file(directory, filename) - 读取某个目录下的某个文件内容\n6. curl(url) - 通过curl访问网页并返回网页内容\n\n当用户请求需要使用这些工具时，请以JSON格式输出工具调用请求，例如：\n{\"tool_call\": {\"name\": \"list_files\", \"params\": {\"directory\": \"/path/to/dir\"}}}"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {env_vars.get('API_KEY', '')}"
    }
    
    # 记录开始时间
    start_time = time.time()
    
    # 根据 scheme 选择连接类型
    if url.scheme == 'https':
        conn = HTTPSConnection(host, timeout=int(env_vars.get('TIMEOUT', 30)))
    else:
        conn = HTTPConnection(host, timeout=int(env_vars.get('TIMEOUT', 30)))
    
    # 发送请求
    conn.request("POST", path, body=json.dumps(data), headers=headers)
    response = conn.getresponse()
    
    # 记录结束时间
    end_time = time.time()
    
    # 读取响应
    response_data = response.read().decode('utf-8')
    conn.close()
    
    # 解析响应
    response_json = json.loads(response_data)
    
    # 计算 token 消耗
    prompt_tokens = response_json.get('usage', {}).get('prompt_tokens', count_tokens(prompt))
    completion_tokens = response_json.get('usage', {}).get('completion_tokens', 0)
    total_tokens = response_json.get('usage', {}).get('total_tokens', prompt_tokens + completion_tokens)
    
    # 计算时间
    elapsed_time = end_time - start_time
    
    # 计算 token/速度
    tokens_per_second = total_tokens / elapsed_time if elapsed_time > 0 else 0
    
    # 提取回复内容
    content = response_json.get('choices', [{}])[0].get('message', {}).get('content', '')
    
    # 检查是否有工具调用请求
    tool_calls = response_json.get('choices', [{}])[0].get('message', {}).get('tool_calls', [])
    
    return {
        "content": content,
        "tool_calls": tool_calls,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "elapsed_time": elapsed_time,
        "tokens_per_second": tokens_per_second
    }

# 执行工具调用
def execute_tool_call(tool_call):
    tool_name = tool_call.get('name')
    params = tool_call.get('params', {})
    
    if tool_name == 'list_files':
        return list_files(params.get('directory'))
    elif tool_name == 'rename_file':
        return rename_file(params.get('directory'), params.get('old_name'), params.get('new_name'))
    elif tool_name == 'delete_file':
        return delete_file(params.get('directory'), params.get('filename'))
    elif tool_name == 'create_file':
        return create_file(params.get('directory'), params.get('filename'), params.get('content'))
    elif tool_name == 'read_file':
        return read_file(params.get('directory'), params.get('filename'))
    elif tool_name == 'curl':
        return curl(params.get('url'))
    else:
        return {"status": "error", "message": f"未知工具: {tool_name}"}

# 处理工具调用并获取最终响应
def process_tool_calls(prompt, env_vars):
    # 第一次调用 LLM 获取工具调用请求
    result = call_llm(prompt, env_vars)
    
    # 检查是否有工具调用请求
    if result.get('tool_calls'):
        # 执行工具调用
        tool_results = []
        for tool_call in result['tool_calls']:
            tool_result = execute_tool_call(tool_call)
            tool_results.append({
                "tool_call_id": tool_call.get('id'),
                "tool_name": tool_call.get('name'),
                "result": tool_result
            })
        
        # 解析 BASE_URL
        url = urlparse(env_vars.get('BASE_URL', 'https://api.openai.com/v1'))
        host = url.netloc
        path = url.path or '/v1'
        if not path.endswith('/'):
            path += '/'
        path += 'chat/completions'
        
        # 构建请求数据，包含工具执行结果
        data = {
            "model": env_vars.get('MODEL', 'gpt-3.5-turbo'),
            "messages": [
                {"role": "system", "content": "你是一个助手，能够使用以下工具来执行文件操作和网络访问：\n\n工具列表：\n1. list_files(directory) - 列出某个目录下的所有文件和文件夹\n2. rename_file(directory, old_name, new_name) - 修改某个目录下某个文件的名字\n3. delete_file(directory, filename) - 删除某个目录下的某个文件\n4. create_file(directory, filename, content) - 在某个目录下新建1个文件，并且写入内容\n5. read_file(directory, filename) - 读取某个目录下的某个文件内容\n6. curl(url) - 通过curl访问网页并返回网页内容\n\n当用户请求需要使用这些工具时，请以JSON格式输出工具调用请求，例如：\n{\"tool_call\": {\"name\": \"list_files\", \"params\": {\"directory\": \"/path/to/dir\"}}}"},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": result['content'], "tool_calls": result['tool_calls']}
            ],
            "temperature": 0.7
        }
        
        # 添加工具执行结果
        for tool_result in tool_results:
            data["messages"].append({
                "role": "tool",
                "tool_call_id": tool_result["tool_call_id"],
                "name": tool_result["tool_name"],
                "content": json.dumps(tool_result["result"])
            })
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {env_vars.get('API_KEY', '')}"
        }
        
        # 记录开始时间
        start_time = time.time()
        
        # 根据 scheme 选择连接类型
        if url.scheme == 'https':
            conn = HTTPSConnection(host, timeout=int(env_vars.get('TIMEOUT', 30)))
        else:
            conn = HTTPConnection(host, timeout=int(env_vars.get('TIMEOUT', 30)))
        
        # 发送请求
        conn.request("POST", path, body=json.dumps(data), headers=headers)
        response = conn.getresponse()
        
        # 记录结束时间
        end_time = time.time()
        
        # 读取响应
        response_data = response.read().decode('utf-8')
        conn.close()
        
        # 解析响应
        response_json = json.loads(response_data)
        
        # 提取最终回复内容
        final_content = response_json.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # 计算总 token 消耗
        total_tokens = response_json.get('usage', {}).get('total_tokens', 0)
        
        return {
            "content": final_content,
            "tool_results": tool_results,
            "total_tokens": total_tokens,
            "elapsed_time": end_time - start_time
        }
    else:
        # 没有工具调用请求，直接返回 LLM 的回复
        return {
            "content": result['content'],
            "tool_results": [],
            "total_tokens": result['total_tokens'],
            "elapsed_time": result['elapsed_time']
        }

if __name__ == "__main__":
    # 加载环境变量
    env_vars = load_env()
    
    # 检查必要的环境变量
    if not env_vars.get('API_KEY'):
        print("请在 .env 文件中设置 API_KEY")
        exit(1)
    
    # 测试提示
    print("请输入您的请求（例如：列出 practice02 目录下的文件）：")
    prompt = input("输入: ")
    
    print(f"\n发送请求到 LLM API...")
    print(f"模型: {env_vars.get('MODEL', 'gpt-3.5-turbo')}")
    print(f"基础 URL: {env_vars.get('BASE_URL', 'https://api.openai.com/v1')}")
    print(f"提示: {prompt}")
    print("=" * 80)
    
    try:
        # 处理工具调用并获取最终响应
        result = process_tool_calls(prompt, env_vars)
        
        # 输出工具执行结果
        if result.get('tool_results'):
            print("工具执行结果:")
            for tool_result in result['tool_results']:
                print(f"- 工具: {tool_result['tool_name']}")
                print(f"  结果: {json.dumps(tool_result['result'], ensure_ascii=False)}")
            print("=" * 80)
        
        # 输出最终回复内容
        print("最终回复内容:")
        print(result["content"])
        print("=" * 80)
        print(f"统计信息:")
        print(f"总 Token 数: {result['total_tokens']}")
        print(f"耗时: {result['elapsed_time']:.2f} 秒")
    except ConnectionRefusedError:
        # 从 BASE_URL 中提取端口
        import urllib.parse
        url = urllib.parse.urlparse(env_vars.get('BASE_URL', 'http://localhost:1234'))
        port = url.port or 1234
        
        print("错误: 无法连接到 LLM 服务器。请确保:")
        print("1. LM Studio 已启动")
        print(f"2. 服务器正在端口 {port} 上运行")
        print("3. BASE_URL 配置正确")
    except Exception as e:
        print(f"错误: {str(e)}")
