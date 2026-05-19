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
    if not isinstance(s, str):
        return s
    
    s = s.replace('\\n', '\n')
    s = s.replace('\\r', '\r')
    s = s.replace('\\t', '\t')
    s = s.replace('\\\\', '\\')
    
    try:
        def replace_unicode(match):
            code = match.group(1)
            return chr(int(code, 16))
        
        s = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, s)
    except:
        pass
    
    return s

# 工具函数：列出目录下的文件
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
            return {"status": "success", "message": "文件已重命名为 %s" % new_name}
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
        content = decode_escaped_string(content)
        
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            written_content = f.read()
        
        return {"status": "success", "message": "文件 %s 已创建" % file_name, "preview": written_content[:200]}
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
        
        url = "http://localhost:3001/api/v1/workspace/%s/chat" % workspace_slug
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % api_key
        }
        
        data = {"message": message}
        
        curl_command = [
            "curl", "-X", "POST", url,
            "-H", "Content-Type: %s" % headers['Content-Type'],
            "-H", "Authorization: %s" % headers['Authorization'],
            "-d", json.dumps(data, ensure_ascii=False)
        ]
        
        result = subprocess.run(curl_command, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            return {"status": "error", "message": "curl执行失败: %s" % result.stderr}
        
        try:
            response_data = json.loads(result.stdout)
            return {"status": "success", "data": response_data}
        except json.JSONDecodeError:
            return {"status": "error", "message": "响应解析失败: %s" % result.stdout}
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
            return {"status": "error", "message": "技能 %s 不存在" % skill_name}
        
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
                prompt += "用户: %s\n" % msg['content']
            elif msg["role"] == "assistant":
                prompt += "AI: %s\n" % msg['content']
        
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
            "Authorization": "Bearer %s" % token
        }
        
        conn.request("POST", "%s/chat/completions" % path, json.dumps(data), headers)
        response = conn.getresponse()
        response_data = json.loads(response.read().decode('utf-8'))
        conn.close()
        
        key_info = response_data['choices'][0]['message']['content']
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("\n=== %s ===\n" % time.strftime('%Y-%m-%d %H:%M:%S'))
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
                prompt += "用户: %s\n" % msg['content']
            elif msg["role"] == "assistant":
                prompt += "AI: %s\n" % msg['content']
        
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
            "Authorization": "Bearer %s" % token
        }
        
        conn.request("POST", "%s/chat/completions" % path, json.dumps(data), headers)
        response = conn.getresponse()
        response_data = json.loads(response.read().decode('utf-8'))
        conn.close()
        
        summary = response_data['choices'][0]['message']['content']
        
        new_history = [history[0]]
        new_history.append({"role": "assistant", "content": "【聊天历史摘要】\n%s" % summary})
        new_history.extend(keep_part)
        
        return new_history
    except Exception as e:
        print("压缩历史记录时出错: %s" % e)
        return history

# 调用LLM（非流式）
def call_llm(prompt, env_vars, history):
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
        "stream": False
    }
    
    conn = http.client.HTTPSConnection(host)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer %s" % token
    }
    
    conn.request("POST", "%s/chat/completions" % path, json.dumps(data), headers)
    response = conn.getresponse()
    response_data = json.loads(response.read().decode('utf-8'))
    conn.close()
    
    return response_data['choices'][0]['message']['content']

# 流式调用LLM
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
        "Authorization": "Bearer %s" % token
    }
    
    conn.request("POST", "%s/chat/completions" % path, json.dumps(data), headers)
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

# ============ 链式工具调用功能 ============

class ChainedCallContext:
    """链式调用上下文管理器，用于在多个工具调用之间传递数据和状态"""
    
    def __init__(self, max_iterations=10):
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.call_history = []
        self.intermediate_variables = {}
        self.final_answer = None
        self.is_complete = False
    
    def add_call(self, tool_name, arguments, result):
        """记录一次工具调用及其结果"""
        call_record = {
            "iteration": self.current_iteration,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.call_history.append(call_record)
    
    def set_variable(self, name, value):
        """设置中间变量"""
        self.intermediate_variables[name] = value
    
    def get_variable(self, name, default=None):
        """获取中间变量"""
        return self.intermediate_variables.get(name, default)
    
    def increment_iteration(self):
        """增加迭代次数"""
        self.current_iteration += 1
    
    def is_max_iterations_reached(self):
        """检查是否达到最大迭代次数"""
        return self.current_iteration >= self.max_iterations
    
    def get_call_history_summary(self):
        """获取调用历史摘要"""
        summary = []
        for record in self.call_history:
            summary.append({
                "tool_name": record["tool_name"],
                "arguments": record["arguments"],
                "status": record["result"].get("status", "unknown")
            })
        return summary

def build_analysis_prompt(user_request, context):
    """构建分析提示词，用于指导LLM进行链式决策"""
    
    history_description = ""
    if context.call_history:
        history_description = "已执行的工具调用历史：\n"
        for i, record in enumerate(context.call_history, 1):
            history_description += "%d. 工具: %s\n" % (i, record['tool_name'])
            history_description += "   参数: %s\n" % json.dumps(record['arguments'], ensure_ascii=False)
            result_summary = record['result'].get('message', '')
            if not result_summary:
                result_summary = str(record['result'])[:100]
            history_description += "   结果: %s\n\n" % result_summary
    
    variables_description = ""
    if context.intermediate_variables:
        variables_description = "当前可用的中间变量：\n"
        for name, value in context.intermediate_variables.items():
            value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            variables_description += "- %s: %s\n" % (name, value_str)
    
    prompt = """
你是一个智能决策助手，需要根据用户请求和已执行的步骤历史，决定下一步操作。

用户原始请求：
%s

%s

%s

决策规则：
1. 分析用户请求和已执行的步骤，判断是否需要继续调用工具
2. 如果已有足够信息回答用户，可以直接完成任务
3. 如果需要更多信息，选择合适的工具进行调用
4. 可以使用之前工具调用的结果作为下一步工具调用的参数
5. 如果连续调用失败或结果重复，应考虑任务完成或报错

输出格式要求（必须是纯JSON）：
- 完成任务时：
{"done": true, "answer": "最终回答内容"}

- 继续调用工具时：
{"done": false, "tool_call": {"name": "工具名称", "arguments": {"参数名": "参数值"}}}

可用工具列表：
1. list_files(directory): 列出指定目录下的所有文件和文件夹
2. rename_file(directory, old_name, new_name): 修改文件名
3. delete_file(directory, file_name): 删除文件
4. create_file(directory, file_name, content): 创建文件
5. read_file(directory, file_name): 读取文件内容
6. fetch_webpage(url): 访问网页并返回内容
7. search_chat_history(query): 搜索聊天历史记录
8. anythingllm_query(message): 查询AnythingLLM文档仓库
9. load_skill_content(skill_name): 加载指定技能的内容

请严格按照JSON格式输出，不要包含任何多余内容！
""" % (user_request, history_description, variables_description)
    
    return prompt.strip()

def execute_tool(tool_name, arguments):
    """执行工具调用"""
    print("\n执行工具：%s" % tool_name)
    print("参数: %s" % json.dumps(arguments, ensure_ascii=False))
    
    try:
        if tool_name == "list_files":
            result = list_files(arguments.get("directory"))
        elif tool_name == "rename_file":
            result = rename_file(arguments.get("directory"), arguments.get("old_name"), arguments.get("new_name"))
        elif tool_name == "delete_file":
            result = delete_file(arguments.get("directory"), arguments.get("file_name"))
        elif tool_name == "create_file":
            if "content" in arguments:
                arguments["content"] = decode_escaped_string(arguments["content"])
            result = create_file(arguments.get("directory"), arguments.get("file_name"), arguments.get("content"))
        elif tool_name == "read_file":
            result = read_file(arguments.get("directory"), arguments.get("file_name"))
        elif tool_name == "fetch_webpage":
            result = fetch_webpage(arguments.get("url"))
        elif tool_name == "search_chat_history":
            result = search_chat_history(arguments.get("query"))
        elif tool_name == "anythingllm_query":
            result = anythingllm_query(arguments.get("message"))
        elif tool_name == "load_skill_content":
            result = load_skill_content(arguments.get("skill_name"))
        else:
            result = {"status": "error", "message": "未知工具: %s" % tool_name}
        
        print("结果状态: %s" % result.get('status', 'unknown'))
        return result
    except Exception as e:
        return {"status": "error", "message": "执行工具时出错: %s" % str(e)}

def execute_chained_tool_call(user_request, env_vars):
    """执行链式工具调用的完整流程"""
    
    context = ChainedCallContext(max_iterations=10)
    history = []
    
    system_prompt = """
你是一个可以进行链式工具调用的AI助手。你需要根据用户的请求，自主决定是否需要调用工具，以及调用哪些工具。

链式调用规则：
1. 你可以根据前一个工具的输出结果，作为后一个工具的输入参数
2. 每次调用工具后，你会收到工具执行结果，并可以根据结果决定下一步操作
3. 如果已经收集到足够的信息，可以直接回答用户，不需要继续调用工具
4. 请仔细分析工具返回的结果，不要忽略任何重要信息
5. 如果任务无法完成或遇到错误，请告知用户

可用工具列表：
1. list_files(directory): 列出指定目录下的所有文件和文件夹
2. rename_file(directory, old_name, new_name): 修改文件名
3. delete_file(directory, file_name): 删除文件
4. create_file(directory, file_name, content): 创建文件
5. read_file(directory, file_name): 读取文件内容
6. fetch_webpage(url): 访问网页并返回内容
7. search_chat_history(query): 搜索聊天历史记录
8. anythingllm_query(message): 查询AnythingLLM文档仓库
9. load_skill_content(skill_name): 加载指定技能的内容

链式调用示例：
场景：用户想查找某个目录下的文件并读取内容
步骤1: list_files("D:\\documents") 获取文件列表
步骤2: read_file("D:\\documents", "report.txt") 读取指定文件
步骤3: 基于文件内容回答用户

输出格式要求（必须是纯JSON）：
- 完成任务时：{"done": true, "answer": "最终回答内容"}
- 继续调用工具时：{"done": false, "tool_call": {"name": "工具名称", "arguments": {"参数名": "参数值"}}}
"""
    
    history.append({"role": "system", "content": system_prompt})
    
    print("开始链式工具调用，用户请求: %s" % user_request)
    
    while not context.is_max_iterations_reached() and not context.is_complete:
        context.increment_iteration()
        print("\n=== 第 %d 轮迭代 ===" % context.current_iteration)
        
        analysis_prompt = build_analysis_prompt(user_request, context)
        
        llm_response = call_llm(analysis_prompt, env_vars, history)
        
        print("LLM决策响应: %s..." % llm_response[:200])
        
        try:
            response_data = json.loads(llm_response)
            
            if response_data.get("done"):
                context.final_answer = response_data.get("answer", "")
                context.is_complete = True
                print("\n任务完成！")
                break
            
            elif "tool_call" in response_data:
                tool_call = response_data["tool_call"]
                tool_name = tool_call.get("name")
                arguments = tool_call.get("arguments", {})
                
                result = execute_tool(tool_name, arguments)
                
                context.add_call(tool_name, arguments, result)
                
                history.append({
                    "role": "assistant",
                    "content": "工具调用: %s, 参数: %s" % (tool_name, json.dumps(arguments, ensure_ascii=False))
                })
                history.append({
                    "role": "user",
                    "content": "工具执行结果: %s" % json.dumps(result, ensure_ascii=False)
                })
                
                if result.get("status") == "success" and "data" in result:
                    context.set_variable("last_tool_result_%s" % tool_name, result["data"])
            
            else:
                print("无法解析LLM响应格式")
                break
                
        except json.JSONDecodeError as e:
            print("解析LLM响应失败: %s" % e)
            context.final_answer = llm_response
            context.is_complete = True
            break
        except Exception as e:
            print("处理LLM响应时出错: %s" % e)
            break
    
    if context.final_answer:
        return {"status": "success", "answer": context.final_answer, "call_history": context.get_call_history_summary()}
    else:
        return {"status": "error", "message": "达到最大迭代次数或执行失败", "call_history": context.get_call_history_summary()}

# 测试函数
def test_chained_calls():
    """测试链式工具调用功能"""
    env_vars = load_env()
    
    if not env_vars.get('TOKEN'):
        print("错误: 请在 .env 文件中设置 TOKEN")
        return
    
    print("=== 测试链式工具调用 ===")
    
    # 测试1：文件搜索链式调用
    print("\n--- 测试1：文件搜索链式调用 ---")
    user_request1 = "请查找 practice06 目录下所有包含'def'关键词的文件，并总结这些文件的主要内容"
    print("用户请求: %s" % user_request1)
    result1 = execute_chained_tool_call(user_request1, env_vars)
    print("\n测试1结果:")
    print("状态: %s" % result1.get('status'))
    if result1.get('answer'):
        print("回答: %s..." % result1['answer'][:500])
    print("调用历史: %s" % json.dumps(result1.get('call_history', []), ensure_ascii=False, indent=2))
    
    # 测试2：技能查询链式调用
    print("\n--- 测试2：技能查询链式调用 ---")
    user_request2 = "我想了解notice技能的详细规则"
    print("用户请求: %s" % user_request2)
    result2 = execute_chained_tool_call(user_request2, env_vars)
    print("\n测试2结果:")
    print("状态: %s" % result2.get('status'))
    if result2.get('answer'):
        print("回答: %s..." % result2['answer'][:500])
    print("调用历史: %s" % json.dumps(result2.get('call_history', []), ensure_ascii=False, indent=2))
    
    # 测试3：网页处理链式调用
    print("\n--- 测试3：网页处理链式调用 ---")
    user_request3 = "访问 https://www.example.com 并总结页面内容，保存到 practice07/summary.txt"
    print("用户请求: %s" % user_request3)
    result3 = execute_chained_tool_call(user_request3, env_vars)
    print("\n测试3结果:")
    print("状态: %s" % result3.get('status'))
    if result3.get('answer'):
        print("回答: %s..." % result3['answer'][:500])
    print("调用历史: %s" % json.dumps(result3.get('call_history', []), ensure_ascii=False, indent=2))

def main():
    env_vars = load_env()
    
    if not env_vars.get('TOKEN'):
        print("错误: 请在 .env 文件中设置 TOKEN")
        return
    
    print("=== AI 链式工具调用终端 ===")
    print("输入 'exit' 退出")
    print("输入 'test' 运行测试")
    print("==========================\n")
    
    try:
        while True:
            user_input = input("你: ").strip()
            if user_input.lower() == 'exit':
                break
            if user_input.lower() == 'test':
                test_chained_calls()
                continue
            if not user_input:
                continue
            
            result = execute_chained_tool_call(user_input, env_vars)
            
            print("\n最终回答:")
            print(result.get("answer", "无法完成请求"))
            
            if result.get("call_history"):
                print("\n调用历史:")
                for i, call in enumerate(result["call_history"], 1):
                    print("%d. %s - %s" % (i, call['tool_name'], call['status']))
            
    except KeyboardInterrupt:
        print("\n退出成功")
    except Exception as e:
        print("\n错误：%s" % e)

if __name__ == "__main__":
    main()
