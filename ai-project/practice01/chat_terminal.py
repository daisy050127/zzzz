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
    
    print("=== AI 聊天终端 ===")
    print("输入 'exit' 或按 Ctrl+C 退出")
    print("==================\n")
    
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
            
            # 限制历史记录长度，避免上下文过长
            if len(history) > 10:  # 最多保留 5 轮对话
                history = history[-10:]
            
    except KeyboardInterrupt:
        print("\n\n退出聊天终端")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()