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

# 确保日志目录和文件存在
def ensure_log_file():
    log_dir = "D:\chat-log"
    log_file = os.path.join(log_dir, "log.txt")
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    if not os.path.exists(log_file):
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("# 聊天关键信息日志\n\n")
    
    return log_file

# 构建系统提示
def build_system_prompt():
    return """
你是一个智能助手，能够帮助用户进行各种对话。

当你收到用户的消息时，请根据上下文进行回答。

如果你收到一个特殊的关键信息提取请求，请按照 5W 规则提取关键信息：
- Who: 谁
- What: 做了什么事
- When: 什么时候（可选）
- Where: 在何处（可选）
- Why: 为什么要做这个事（可选）

如果你收到一个特殊的搜索请求，请根据提供的聊天历史和用户的查询，给出相关的回答。
"""

# 构建关键信息提取提示
def build_keyinfo_prompt(history):
    return f"""
请从以下聊天历史中提取关键信息，按照 5W 规则（Who、What、When、Where、Why）进行提取：

{json.dumps(history, ensure_ascii=False, indent=2)}

提取要求：
1. 提取多条关键信息
2. 每条信息都按照 5W 规则组织
3. 只提取重要的信息，忽略无关细节
4. 用自然语言描述，不要使用列表格式
"""

# 构建搜索提示
def build_search_prompt(log_content, user_query):
    return f"""
请根据以下聊天历史日志和用户的查询，给出相关的回答：

聊天历史日志：
{log_content}

用户查询：
{user_query}

回答要求：
1. 基于聊天历史日志中的信息进行回答
2. 回答要准确、详细
3. 如果日志中没有相关信息，请如实告知
"""

# 流式访问 LLM API
def call_llm_stream(prompt, env_vars, history):
    base_url = env_vars.get('BASE_URL', 'https://api.openai.com/v1')
    model = env_vars.get('MODEL', 'gpt-3.5-turbo')
    token = env_vars.get('TOKEN', '')
    temperature = float(env_vars.get('TEMPERATURE', 0.7))
    max_tokens = int(env_vars.get('MAX_TOKENS', 2000))
    
    # 解析 URL
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    
    # 构建消息列表（包含历史记录）
    messages = []
    # 添加系统提示
    messages.append({"role": "system", "content": build_system_prompt()})
    # 添加历史记录
    for msg in history:
        messages.append(msg)
    # 添加用户输入
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
                        full_response += content
                        assistant_message += content
            except json.JSONDecodeError:
                pass
    
    conn.close()
    
    # 返回完整响应和助手消息
    return full_response, assistant_message

# 提取关键信息并保存到日志
def extract_keyinfo(history, env_vars):
    print("\n[系统] 每五次聊天，正在提取关键信息...")
    
    # 构建关键信息提取提示
    keyinfo_prompt = build_keyinfo_prompt(history)
    
    # 调用 LLM 提取关键信息
    keyinfo, _ = call_llm_stream(keyinfo_prompt, env_vars, [])
    
    print(f"[系统] 关键信息提取完成")
    
    # 保存到日志文件
    log_file = ensure_log_file()
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"# {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(keyinfo)
        f.write("\n\n")
    
    print(f"[系统] 关键信息已保存到 {log_file}")

# 搜索聊天历史
def search_chat_history(user_query, env_vars):
    print("\n[系统] 正在搜索聊天历史...")
    
    # 读取日志文件
    log_file = ensure_log_file()
    with open(log_file, 'r', encoding='utf-8') as f:
        log_content = f.read()
    
    # 构建搜索提示
    search_prompt = build_search_prompt(log_content, user_query)
    
    # 调用 LLM 进行搜索
    search_result, _ = call_llm_stream(search_prompt, env_vars, [])
    
    print("[系统] 搜索完成")
    return search_result

def main():
    # 加载环境变量
    env_vars = load_env()
    
    if not env_vars.get('TOKEN'):
        print("错误: 请在 .env 文件中设置 TOKEN")
        print("提示: 复制 .env.example 为 .env 并填写正确的 API 密钥")
        return
    
    # 初始化历史记录
    history = []
    chat_count = 0
    
    print("=== AI 聊天终端（带关键信息提取和历史搜索）===")
    print("输入 'exit' 或按 Ctrl+C 退出")
    print("每五次聊天会自动提取关键信息并保存到 D:\chat-log\log.txt")
    print("输入以 '/search' 开头的消息或表达'查找聊天历史'的意思，可搜索聊天历史")
    print("==================\n")
    
    try:
        while True:
            # 获取用户输入
            user_input = input("你: ").strip()
            
            if user_input.lower() == 'exit':
                break
            
            if not user_input:
                continue
            
            # 检查是否是搜索请求
            if user_input.startswith('/search') or '查找聊天历史' in user_input or '搜索聊天记录' in user_input:
                # 执行搜索
                search_result = search_chat_history(user_input, env_vars)
                print(f"\nAI: {search_result}")
                # 不将搜索请求添加到聊天历史
                continue
            
            # 调用 LLM API（流式）
            print("\nAI: ", end="", flush=True)
            full_response, assistant_message = call_llm_stream(user_input, env_vars, history)
            print(assistant_message)
            
            # 更新历史记录
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": assistant_message})
            chat_count += 1
            
            # 每五次聊天提取一次关键信息
            if chat_count % 5 == 0:
                extract_keyinfo(history, env_vars)
            
    except KeyboardInterrupt:
        print("\n\n退出聊天终端")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()