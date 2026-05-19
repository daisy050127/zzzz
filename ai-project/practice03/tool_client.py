import os
import json
import http.client
from urllib.parse import urlparse
import sys
import time

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
                    # 移除引号
                    value = value.strip('"\'')
                    env_vars[key] = value
    return env_vars

# 工具函数：列出目录下的文件（包括属性和大小）
def list_files(directory):
    try:
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                stat = os.stat(item_path)
                files.append({
                    "name": item,
                    "size": stat.st_size,
                    "mtime": time.ctime(stat.st_mtime),
                    "is_file": True
                })
            elif os.path.isdir(item_path):
                files.append({
                    "name": item,
                    "size": 0,
                    "mtime": time.ctime(os.stat(item_path).st_mtime),
                    "is_file": False
                })
        return {"status": "success", "data": files}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数：修改文件名
def rename_file(directory, old_name, new_name):
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            return {"status": "success", "message": f"文件已重命名为 {new_name}"}
        else:
            return {"status": "error", "message": "文件不存在"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数：删除文件
def delete_file(directory, file_name):
    try:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            return {"status": "success", "message": "文件已删除"}
        else:
            return {"status": "error", "message": "文件不存在"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数：新建文件并写入内容
def create_file(directory, file_name, content):
    try:
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": f"文件 {file_name} 已创建"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数：读取文件内容
def read_file(directory, file_name):
    try:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"status": "success", "data": content}
        else:
            return {"status": "error", "message": "文件不存在"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数：访问网页并返回内容
def fetch_webpage(url):
    try:
        # 解析 URL
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        host = parsed_url.netloc
        path = parsed_url.path or '/'
        query = parsed_url.query
        if query:
            path += '?' + query
        
        # 创建连接
        if scheme == 'https':
            conn = http.client.HTTPSConnection(host)
        else:
            conn = http.client.HTTPConnection(host)
        
        # 发送请求
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        conn.request("GET", path, headers=headers)
        
        # 获取响应
        response = conn.getresponse()
        
        # 读取响应内容
        content = response.read().decode('utf-8', errors='ignore')
        
        conn.close()
        
        # 限制返回内容长度，避免过大
        max_content_length = 10000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n... (内容过长，已截断)"
        
        return {"status": "success", "data": content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 流式访问 LLM API
def call_llm_stream(prompt, env_vars, history):
    base_url = env_vars.get('BASE_URL', 'https://api.openai.com/v1')
    model = env_vars.get('MODEL', 'gpt-3.5-turbo')
    token = env_vars.get('TOKEN', '')
    temperature = float(env_vars.get('TEMPERATURE', 0.7))
    max_tokens = int(env_vars.get('MAX_TOKENS', 1000))
    
    # 解析 URL
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    
    # 构建消息列表（包含历史记录）
    messages = []
    for msg in history:
        messages.append(msg)
    messages.append({"role": "user", "content": prompt})
    
    # 构建请求数据
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True  # 启用流式输出
    }
    
    # 创建连接
    conn = http.client.HTTPSConnection(host)
    
    # 发送请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    conn.request(
        "POST", 
        f"{path}/chat/completions", 
        json.dumps(data), 
        headers
    )
    
    # 获取响应
    response = conn.getresponse()
    
    # 处理流式响应
    full_response = ""
    assistant_message = ""
    
    print("\nAI: ", end="", flush=True)
    
    for line in response:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data_part = line[6:].strip()
            if data_part == '[DONE]':
                break
            try:
                chunk = json.loads(data_part)
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    delta = chunk['choices'][0].get('delta', {})
                    if 'content' in delta:
                        content = delta['content']
                        print(content, end="", flush=True)
                        full_response += content
                        assistant_message += content
            except json.JSONDecodeError:
                pass
    
    conn.close()
    print()  # 换行
    
    # 返回完整响应和助手消息
    return full_response, assistant_message

def main():
    # 加载环境变量
    env_vars = load_env()
    
    if not env_vars.get('TOKEN'):
        print("错误: 请在 .env 文件中设置 TOKEN")
        print("提示: 复制 .env.example 为 .env 并填写正确的 API 密钥")
        return
    
    # 初始化历史记录
    history = []
    
    # 系统提示词，包含工具调用说明
    system_prompt = """
你是一个可以调用工具的AI助手。我提供了以下工具供你使用：

1. list_files(directory): 列出指定目录下的所有文件和文件夹，返回包含文件名称、大小、修改时间等信息的列表
   - 参数：directory (字符串) - 要列出的目录路径
   - 返回：包含文件信息的字典

2. rename_file(directory, old_name, new_name): 修改指定目录下的文件名称
   - 参数：
     - directory (字符串) - 文件所在目录
     - old_name (字符串) - 原文件名称
     - new_name (字符串) - 新文件名称
   - 返回：操作结果

3. delete_file(directory, file_name): 删除指定目录下的文件
   - 参数：
     - directory (字符串) - 文件所在目录
     - file_name (字符串) - 要删除的文件名称
   - 返回：操作结果

4. create_file(directory, file_name, content): 在指定目录下创建新文件并写入内容
   - 参数：
     - directory (字符串) - 要创建文件的目录
     - file_name (字符串) - 新文件名称
     - content (字符串) - 要写入的文件内容
   - 返回：操作结果

5. read_file(directory, file_name): 读取指定目录下文件的内容
   - 参数：
     - directory (字符串) - 文件所在目录
     - file_name (字符串) - 要读取的文件名称
   - 返回：文件内容

6. fetch_webpage(url): 访问指定的网页并返回网页内容
   - 参数：
     - url (字符串) - 要访问的网页URL
   - 返回：网页内容

当用户请求需要使用这些工具时，请以JSON格式输出工具调用请求，格式如下：
{"tool_call": {"name": "工具名称", "params": {"参数1": "值1", "参数2": "值2"}}}

当我返回工具执行结果后，请根据结果提供最终回答。
"""
    
    # 将系统提示词添加到历史记录
    history.append({"role": "system", "content": system_prompt})
    
    print("=== AI 工具调用终端 ===")
    print("输入 'exit' 或按 Ctrl+C 退出")
    print("可用工具: list_files, rename_file, delete_file, create_file, read_file, fetch_webpage")
    print("======================\n")
    
    try:
        while True:
            # 获取用户输入
            user_input = input("你: ").strip()
            
            if user_input.lower() == 'exit':
                break
            
            if not user_input:
                continue
            
            # 调用 LLM API（流式）
            full_response, assistant_message = call_llm_stream(user_input, env_vars, history)
            
            # 更新历史记录
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": assistant_message})
            
            # 检查是否需要执行工具调用
            if 'tool_call' in full_response:
                try:
                    # 解析工具调用请求
                    tool_call_data = json.loads(full_response)
                    if 'tool_call' in tool_call_data:
                        tool_name = tool_call_data['tool_call']['name']
                        params = tool_call_data['tool_call']['params']
                        
                        print(f"\n执行工具: {tool_name}")
                        
                        # 执行相应的工具
                        if tool_name == 'list_files':
                            result = list_files(params.get('directory'))
                        elif tool_name == 'rename_file':
                            result = rename_file(params.get('directory'), params.get('old_name'), params.get('new_name'))
                        elif tool_name == 'delete_file':
                            result = delete_file(params.get('directory'), params.get('file_name'))
                        elif tool_name == 'create_file':
                            result = create_file(params.get('directory'), params.get('file_name'), params.get('content'))
                        elif tool_name == 'read_file':
                            result = read_file(params.get('directory'), params.get('file_name'))
                        elif tool_name == 'fetch_webpage':
                            result = fetch_webpage(params.get('url'))
                        else:
                            result = {"status": "error", "message": "未知工具"}
                        
                        print(f"工具执行结果: {json.dumps(result, ensure_ascii=False)}")
                        
                        # 将工具执行结果添加到历史记录
                        history.append({"role": "user", "content": f"工具执行结果: {json.dumps(result, ensure_ascii=False)}"})
                        
                        # 再次调用 LLM 获取最终回答
                        final_response, _ = call_llm_stream("", env_vars, history)
                        history.append({"role": "assistant", "content": final_response})
                except json.JSONDecodeError:
                    pass
            
            # 限制历史记录长度，避免上下文过长
            if len(history) > 20:  # 最多保留 10 轮对话
                history = history[-20:]
            
    except KeyboardInterrupt:
        print("\n\n退出工具调用终端")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()