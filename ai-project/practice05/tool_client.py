import os
import json
import http.client
from urllib.parse import urlparse
import sys
import time
import subprocess

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

# 工具函数：搜索聊天历史
def search_chat_history(query):
    try:
        # 定义日志文件路径
        log_dir = "D:\\chat-log"
        log_file = os.path.join(log_dir, "log.txt")
        
        # 检查日志文件是否存在
        if not os.path.exists(log_file):
            return {"status": "error", "message": "聊天历史记录不存在"}
        
        # 读取日志文件内容
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        return {"status": "success", "data": log_content, "query": query}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数：查询AnythingLLM文档仓库
def anythingllm_query(message):
    try:
        # 加载环境变量
        env_vars = load_env()
        api_key = env_vars.get('ANYTHINGLLM_API_KEY')
        workspace_slug = env_vars.get('ANYTHINGLLM_WORKSPACE_SLUG')
        
        if not api_key or not workspace_slug:
            return {"status": "error", "message": "请在.env文件中设置ANYTHINGLLM_API_KEY和ANYTHINGLLM_WORKSPACE_SLUG"}
        
        # 构建curl命令
        url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 构建请求数据
        data = {
            "message": message
        }
        
        # 构建curl命令字符串
        curl_command = [
            "curl",
            "-X", "POST",
            url,
            "-H", f"Content-Type: {headers['Content-Type']}",
            "-H", f"Authorization: {headers['Authorization']}",
            "-d", json.dumps(data, ensure_ascii=False)
        ]
        
        # 执行curl命令
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 检查执行结果
        if result.returncode != 0:
            return {"status": "error", "message": f"curl执行失败: {result.stderr}"}
        
        # 解析响应
        try:
            response_data = json.loads(result.stdout)
            return {"status": "success", "data": response_data}
        except json.JSONDecodeError:
            return {"status": "error", "message": f"响应解析失败: {result.stdout}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 函数：计算聊天历史长度
def calculate_history_length(history):
    length = 0
    for msg in history:
        if "content" in msg:
            length += len(msg["content"])
    return length

# 函数：提取关键信息并保存到日志
def extract_key_info(history, env_vars):
    try:
        # 定义日志文件路径
        log_dir = "D:\\chat-log"
        log_file = os.path.join(log_dir, "log.txt")
        
        # 确保目录存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 准备提取关键信息的提示
        prompt = "请从以下聊天历史中提取关键信息，按照5W规则（Who、What、When、Where、Why）提取。\n\n聊天历史：\n"
        
        # 只提取最近的聊天内容
        recent_history = history[-10:]  # 最近5轮对话
        for msg in recent_history:
            if msg["role"] == "user":
                prompt += f"用户: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt += f"AI: {msg['content']}\n"
        
        prompt += "\n请按照5W规则提取关键信息，每个关键信息单独一行，格式为：\nWho: ...\nWhat: ...\nWhen: ...（可选）\nWhere: ...（可选）\nWhy: ...（可选）\n"
        
        # 调用LLM提取关键信息
        messages = [{"role": "user", "content": prompt}]
        
        base_url = env_vars.get('BASE_URL', 'https://api.openai.com/v1')
        model = env_vars.get('MODEL', 'gpt-3.5-turbo')
        token = env_vars.get('TOKEN', '')
        
        # 解析 URL
        parsed_url = urlparse(base_url)
        host = parsed_url.netloc
        path = parsed_url.path or '/'
        
        # 构建请求数据
        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 500,
            "stream": False
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
        response_data = json.loads(response.read().decode('utf-8'))
        conn.close()
        
        # 提取关键信息
        key_info = response_data['choices'][0]['message']['content']
        
        # 保存到日志文件（追加模式）
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            f.write(key_info)
            f.write("\n")
        
        return {"status": "success", "message": "关键信息已提取并保存"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 函数：压缩聊天历史
def compress_history(history, env_vars):
    try:
        # 计算历史记录的70%和30%
        total_messages = len(history) - 1  # 减去系统提示
        if total_messages <= 1:
            return history
        
        # 确定压缩部分和保留部分
        compress_count = int(total_messages * 0.7)
        keep_count = total_messages - compress_count
        
        # 提取需要压缩的部分（前70%）
        compress_part = history[1:compress_count+1]  # 从系统提示之后开始
        keep_part = history[-keep_count:]  # 保留最后30%
        
        # 准备压缩提示
        prompt = "请将以下聊天历史压缩为简洁的摘要，保留关键信息：\n\n"
        for msg in compress_part:
            if msg["role"] == "user":
                prompt += f"用户: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt += f"AI: {msg['content']}\n"
        
        # 调用LLM进行压缩
        messages = [{"role": "user", "content": prompt}]
        
        base_url = env_vars.get('BASE_URL', 'https://api.openai.com/v1')
        model = env_vars.get('MODEL', 'gpt-3.5-turbo')
        token = env_vars.get('TOKEN', '')
        
        # 解析 URL
        parsed_url = urlparse(base_url)
        host = parsed_url.netloc
        path = parsed_url.path or '/'
        
        # 构建请求数据
        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 500,
            "stream": False
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
        response_data = json.loads(response.read().decode('utf-8'))
        conn.close()
        
        # 提取压缩后的摘要
        summary = response_data['choices'][0]['message']['content']
        
        # 构建新的历史记录
        new_history = [history[0]]  # 保留系统提示
        new_history.append({"role": "assistant", "content": f"【聊天历史摘要】\n{summary}"})
        new_history.extend(keep_part)
        
        return new_history
    except Exception as e:
        print(f"压缩历史记录时出错: {e}")
        return history

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
    
    # 计数器
    chat_count = 0
    
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

7. search_chat_history(query): 搜索聊天历史记录
   - 参数：
     - query (字符串) - 搜索查询
   - 返回：聊天历史记录和查询结果

8. anythingllm_query(message): 查询AnythingLLM文档仓库
   - 参数：
     - message (字符串) - 查询消息
   - 返回：文档仓库的查询结果

当用户请求需要使用这些工具时，请以JSON格式输出工具调用请求，格式如下：
{"tool_call": {"name": "工具名称", "params": {"参数1": "值1", "参数2": "值2"}}}

当我返回工具执行结果后，请根据结果提供最终回答。

特别注意：
1. 当用户发送的信息以"/search"开头，或用户表达了"查找聊天历史"的意思，或你认为应该查找聊天历史时，请使用search_chat_history工具。
2. 当用户提到"文档仓库"、"文件仓库"、"仓库"时，请使用anythingllm_query工具。
"""
    
    # 将系统提示词添加到历史记录
    history.append({"role": "system", "content": system_prompt})
    
    print("=== AI 工具调用终端 ===")
    print("输入 'exit' 或按 Ctrl+C 退出")
    print("可用工具: list_files, rename_file, delete_file, create_file, read_file, fetch_webpage, search_chat_history, anythingllm_query")
    print("使用 '/search' 开头的消息可以搜索聊天历史")
    print("提到'文档仓库'、'文件仓库'、'仓库'时会查询AnythingLLM文档仓库")
    print("======================\n")
    
    try:
        while True:
            # 获取用户输入
            user_input = input("你: ").strip()
            
            if user_input.lower() == 'exit':
                break
            
            if not user_input:
                continue
            
            # 检查是否需要搜索聊天历史
            if user_input.startswith('/search') or '查找聊天历史' in user_input or '搜索历史' in user_input:
                # 提取搜索查询
                query = user_input[7:] if user_input.startswith('/search') else user_input
                
                print("\n执行工具: search_chat_history")
                result = search_chat_history(query)
                print(f"工具执行结果: {json.dumps(result, ensure_ascii=False)}")
                
                # 将工具执行结果添加到历史记录
                history.append({"role": "user", "content": user_input})
                history.append({"role": "user", "content": f"工具执行结果: {json.dumps(result, ensure_ascii=False)}"})
                
                # 调用 LLM 获取搜索结果的回答
                final_response, _ = call_llm_stream("", env_vars, history)
                history.append({"role": "assistant", "content": final_response})
                
                # 增加聊天计数
                chat_count += 1
            else:
                # 调用 LLM API（流式）
                full_response, assistant_message = call_llm_stream(user_input, env_vars, history)
                
                # 更新历史记录
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": assistant_message})
                
                # 增加聊天计数
                chat_count += 1
                
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
                            elif tool_name == 'search_chat_history':
                                result = search_chat_history(params.get('query'))
                            elif tool_name == 'anythingllm_query':
                                result = anythingllm_query(params.get('message'))
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
            
            # 检查是否需要提取关键信息（每5次聊天）
            if chat_count % 5 == 0:
                print("\n正在提取关键信息...")
                result = extract_key_info(history, env_vars)
                print(f"关键信息提取结果: {result.get('message')}")
            
            # 检查是否需要压缩聊天历史
            history_length = calculate_history_length(history)
            total_messages = len(history) - 1  # 减去系统提示
            
            if total_messages > 5 or history_length > 3000:
                print("\n正在压缩聊天历史...")
                history = compress_history(history, env_vars)
                print("聊天历史压缩完成")
            
            # 限制历史记录长度，避免上下文过长
            if len(history) > 30:  # 最多保留 15 轮对话
                history = history[-30:]
            
    except KeyboardInterrupt:
        print("\n\n退出工具调用终端")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()