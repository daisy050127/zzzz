import os
import json
import http.client
from urllib.parse import urlparse
import sys
import time
import subprocess
import re

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
                    value = value.strip('"\'')
                    env_vars[key] = value
    return env_vars

# 彻底解码转义字符串
def decode_escaped_string(s):
    """彻底解码各种转义字符"""
    if not isinstance(s, str):
        return s
    
    # 处理换行符
    s = s.replace('\\n', '\n')
    s = s.replace('\\r', '\r')
    s = s.replace('\\t', '\t')
    s = s.replace('\\\\', '\\')
    
    # 处理 Unicode 转义 (如 \uXXXX)
    try:
        # 使用正则表达式处理 \u 转义
        def replace_unicode(match):
            code = match.group(1)
            return chr(int(code, 16))
        
        s = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, s)
    except:
        pass
    
    return s

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

# 工具函数：新建文件并写入内容（彻底修复）
def create_file(directory, file_name, content):
    try:
        # 彻底解码内容
        content = decode_escaped_string(content)
        
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 验证写入的内容
        with open(file_path, 'r', encoding='utf-8') as f:
            written_content = f.read()
        
        return {"status": "success", "message": f"文件 {file_name} 已创建", "preview": written_content[:200]}
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
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        host = parsed_url.netloc
        path = parsed_url.path or '/'
        query = parsed_url.query
        if query:
            path += '?' + query
        
        if scheme == 'https':
            conn = http.client.HTTPSConnection(host)
        else:
            conn = http.client.HTTPConnection(host)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        conn.request("GET", path, headers=headers)
        response = conn.getresponse()
        content = response.read().decode('utf-8', errors='ignore')
        conn.close()
        
        max_content_length = 10000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n... (内容过长，已截断)"
        
        return {"status": "success", "data": content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数：搜索聊天历史
def search_chat_history(query):
    try:
        log_dir = "D:\\chat-log"
        log_file = os.path.join(log_dir, "log.txt")
        
        if not os.path.exists(log_file):
            return {"status": "error", "message": "聊天历史记录不存在"}
        
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        return {"status": "success", "data": log_content, "query": query}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数：查询AnythingLLM文档仓库
def anythingllm_query(message):
    try:
        env_vars = load_env()
        api_key = env_vars.get('ANYTHINGLLM_API_KEY')
        workspace_slug = env_vars.get('ANYTHINGLLM_WORKSPACE_SLUG')
        
        if not api_key or not workspace_slug:
            return {"status": "error", "message": "请在.env文件中设置ANYTHINGLLM_API_KEY和ANYTHINGLLM_WORKSPACE_SLUG"}
        
        url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {"message": message}
        
        curl_command = [
            "curl", "-X", "POST", url,
            "-H", f"Content-Type: {headers['Content-Type']}",
            "-H", f"Authorization: {headers['Authorization']}",
            "-d", json.dumps(data, ensure_ascii=False)
        ]
        
        result = subprocess.run(curl_command, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            return {"status": "error", "message": f"curl执行失败: {result.stderr}"}
        
        try:
            response_data = json.loads(result.stdout)
            return {"status": "success", "data": response_data}
        except json.JSONDecodeError:
            return {"status": "error", "message": f"响应解析失败: {result.stdout}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数：列出可用技能
def list_available_skills():
    try:
        skills_dir = r"D:\ttll\.agents\skills"
        skills = []
        
        if not os.path.exists(skills_dir):
            return {"status": "success", "data": skills}
        
        for skill_name in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill_name)
            if os.path.isdir(skill_path):
                skill_file = os.path.join(skill_path, "SKILL.md")
                if os.path.exists(skill_file):
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if content.startswith('---'):
                        front_matter_end = content.find('---', 3)
                        if front_matter_end != -1:
                            front_matter = content[3:front_matter_end].strip()
                            skill_info = {}
                            for line in front_matter.split('\n'):
                                line = line.strip()
                                if line and ':' in line:
                                    key, value = line.split(':', 1)
                                    key = key.strip()
                                    value = value.strip().strip('"\'')
                                    if key == 'name':
                                        skill_info['name'] = value
                                    elif key == 'description':
                                        skill_info['description'] = value
                            if 'name' in skill_info:
                                skills.append(skill_info)
        
        return {"status": "success", "data": skills}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 工具函数：加载技能内容
def load_skill_content(skill_name):
    try:
        skills_dir = r"D:\ttll\.agents\skills"
        skill_path = os.path.join(skills_dir, skill_name)
        skill_file = os.path.join(skill_path, "SKILL.md")
        
        if not os.path.exists(skill_file):
            return {"status": "error", "message": f"技能 {skill_name} 不存在"}
        
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.startswith('---'):
            front_matter_end = content.find('---', 3)
            if front_matter_end != -1:
                skill_content = content[front_matter_end + 3:].strip()
                return {"status": "success", "data": skill_content}
        
        return {"status": "success", "data": content}
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
        log_dir = "D:\\chat-log"
        log_file = os.path.join(log_dir, "log.txt")
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        prompt = "请从以下聊天历史中提取关键信息，按照5W规则（Who、What、When、Where、Why）提取。\n\n聊天历史：\n"
        recent_history = history[-10:]
        for msg in recent_history:
            if msg["role"] == "user":
                prompt += f"用户: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt += f"AI: {msg['content']}\n"
        
        prompt += "\n请按照5W规则提取关键信息，每个关键信息单独一行，格式为：\nWho: ...\nWhat: ...\nWhen: ...（可选）\nWhere: ...（可选）\nWhy: ...（可选）\n"
        
        messages = [{"role": "user", "content": prompt}]
        base_url = env_vars.get('BASE_URL', 'https://api.openai.com/v1')
        model = env_vars.get('MODEL', 'gpt-3.5-turbo')
        token = env_vars.get('TOKEN', '')
        
        parsed_url = urlparse(base_url)
        host = parsed_url.netloc
        path = parsed_url.path or '/'
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 500,
            "stream": False
        }
        
        conn = http.client.HTTPSConnection(host)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        conn.request("POST", f"{path}/chat/completions", json.dumps(data), headers)
        response = conn.getresponse()
        response_data = json.loads(response.read().decode('utf-8'))
        conn.close()
        
        key_info = response_data['choices'][0]['message']['content']
        
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
        total_messages = len(history) - 1
        if total_messages <= 1:
            return history
        
        compress_count = int(total_messages * 0.7)
        keep_count = total_messages - compress_count
        
        compress_part = history[1:compress_count+1]
        keep_part = history[-keep_count:]
        
        prompt = "请将以下聊天历史压缩为简洁的摘要，保留关键信息：\n\n"
        for msg in compress_part:
            if msg["role"] == "user":
                prompt += f"用户: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt += f"AI: {msg['content']}\n"
        
        messages = [{"role": "user", "content": prompt}]
        base_url = env_vars.get('BASE_URL', 'https://api.openai.com/v1')
        model = env_vars.get('MODEL', 'gpt-3.5-turbo')
        token = env_vars.get('TOKEN', '')
        
        parsed_url = urlparse(base_url)
        host = parsed_url.netloc
        path = parsed_url.path or '/'
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 500,
            "stream": False
        }
        
        conn = http.client.HTTPSConnection(host)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        conn.request("POST", f"{path}/chat/completions", json.dumps(data), headers)
        response = conn.getresponse()
        response_data = json.loads(response.read().decode('utf-8'))
        conn.close()
        
        summary = response_data['choices'][0]['message']['content']
        
        new_history = [history[0]]
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
    
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    
    messages = []
    for msg in history:
        messages.append(msg)
    if prompt.strip():
        messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True
    }
    
    conn = http.client.HTTPSConnection(host)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    conn.request("POST", f"{path}/chat/completions", json.dumps(data), headers)
    response = conn.getresponse()
    
    full_response = ""
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
            except json.JSONDecodeError:
                pass
    
    conn.close()
    print()
    
    return full_response

def main():
    env_vars = load_env()
    
    if not env_vars.get('TOKEN'):
        print("错误: 请在 .env 文件中设置 TOKEN")
        return
    
    history = []
    chat_count = 0
    
    skills_result = list_available_skills()
    skills_list = skills_result.get('data', [])
    skills_json = json.dumps({"skills": skills_list}, ensure_ascii=False)
    
    tool_format_example = '{"tool_call": {"name": "工具名称", "params": {"参数1": "值1", "参数2": "值2"}}}'
    
    system_prompt = f"""
你是一个可以调用工具的AI助手。我提供了以下工具供你使用：

1. list_files(directory): 列出指定目录下的所有文件和文件夹
2. rename_file(directory, old_name, new_name): 修改文件名
3. delete_file(directory, file_name): 删除文件
4. create_file(directory, file_name, content): 创建文件
5. read_file(directory, file_name): 读取文件
6. fetch_webpage(url): 访问网页
7. search_chat_history(query): 搜索聊天历史
8. anythingllm_query(message): 查询文档仓库
9. load_skill_content(skill_name): 加载技能

可用技能：
{skills_json}

当需要使用工具时，**只输出纯JSON格式的工具调用指令，不要输出任何多余文字**，格式如下：
{tool_format_example}

**重要：在生成文件内容时，请直接使用正常的换行符和中文，不要使用转义字符。**
**注意：不要将换行符写成\\\\n，直接写真实的换行。**

收到工具结果后，再给用户自然语言回答。

规则：
1. 用户说 /search 或查找历史 → 使用 search_chat_history
2. 用户提到文档/仓库 → 使用 anythingllm_query
3. 用户要写通知 → 使用 load_skill_content 加载 notice 技能
"""
    
    history.append({"role": "system", "content": system_prompt})
    
    print("=== AI 工具调用终端 ===")
    print("输入 'exit' 退出")
    print("======================\n")
    
    try:
        while True:
            user_input = input("你: ").strip()
            if user_input.lower() == 'exit':
                break
            if not user_input:
                continue
            
            # 先把用户消息加入历史
            history.append({"role": "user", "content": user_input})
            
            # 调用AI
            ai_reply = call_llm_stream("", env_vars, history)
            
            # 判断是否是工具调用
            is_tool_call = False
            tool_result = None
            
            try:
                # 尝试解析 JSON
                # 直接使用原始响应，因为 AI 可能已经输出了正确的 JSON
                stripped = ai_reply.strip()
                if stripped.startswith("{") and stripped.endswith("}"):
                    tool_data = json.loads(stripped)
                    if "tool_call" in tool_data:
                        is_tool_call = True
                        tc = tool_data["tool_call"]
                        tool_name = tc["name"]
                        params = tc.get("params", {})

                        print(f"\n⚙️ 正在执行工具：{tool_name}")
                        
                        # 执行工具
                        if tool_name == "list_files":
                            tool_result = list_files(params.get("directory"))
                        elif tool_name == "rename_file":
                            tool_result = rename_file(params.get("directory"), params.get("old_name"), params.get("new_name"))
                        elif tool_name == "delete_file":
                            tool_result = delete_file(params.get("directory"), params.get("file_name"))
                        elif tool_name == "create_file":
                            # 对 content 参数进行额外解码
                            if "content" in params:
                                params["content"] = decode_escaped_string(params["content"])
                            tool_result = create_file(params.get("directory"), params.get("file_name"), params.get("content"))
                        elif tool_name == "read_file":
                            tool_result = read_file(params.get("directory"), params.get("file_name"))
                        elif tool_name == "fetch_webpage":
                            tool_result = fetch_webpage(params.get("url"))
                        elif tool_name == "search_chat_history":
                            tool_result = search_chat_history(params.get("query"))
                        elif tool_name == "anythingllm_query":
                            tool_result = anythingllm_query(params.get("message"))
                        elif tool_name == "load_skill_content":
                            tool_result = load_skill_content(params.get("skill_name"))
                        else:
                            tool_result = {"status": "error", "message": "未知工具"}
                        
                        if tool_result and tool_result.get("status") == "success" and tool_name == "create_file":
                            print(f"\n✅ 文件已创建，内容预览：\n{tool_result.get('preview', '')}")
            except json.JSONDecodeError as e:
                # 不是有效的 JSON，不是工具调用
                pass
            except Exception as e:
                print(f"\n⚠️ 解析工具调用时出错: {e}")
            
            # 如果是工具调用，把结果发给AI，让AI生成最终回答
            if is_tool_call and tool_result is not None:
                # 把工具结果加入对话
                history.append({"role": "assistant", "content": ai_reply})
                history.append({
                    "role": "user",
                    "content": "工具执行结果：" + str(tool_result)
                })
                # 让AI重新回答
                final_answer = call_llm_stream("", env_vars, history)
                history.append({"role": "assistant", "content": final_answer})
            else:
                # 普通对话，直接保存
                history.append({"role": "assistant", "content": ai_reply})
            
            chat_count += 1
            
            # 每5次提取信息
            if chat_count % 5 == 0:
                print("\n📝 正在自动提取聊天关键信息...")
                extract_key_info(history, env_vars)
            
            # 超长自动压缩
            if len(history) > 20 or calculate_history_length(history) > 2500:
                print("\n🧹 上下文过长，正在自动压缩...")
                history = compress_history(history, env_vars)
            
            # 限制最大长度
            if len(history) > 30:
                history = [history[0]] + history[-29:]
            
    except KeyboardInterrupt:
        print("\n退出成功")
    except Exception as e:
        print(f"\n错误：{e}")

if __name__ == "__main__":
    main()