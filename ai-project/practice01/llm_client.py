import os
import json
import http.client
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
                    # 移除引号
                    value = value.strip('"\'')
                    env_vars[key] = value
    return env_vars

# 访问 LLM API
def call_llm(prompt, env_vars):
    base_url = env_vars.get('BASE_URL', 'https://api.openai.com/v1')
    model = env_vars.get('MODEL', 'gpt-3.5-turbo')
    token = env_vars.get('TOKEN', '')
    temperature = float(env_vars.get('TEMPERATURE', 0.7))
    max_tokens = int(env_vars.get('MAX_TOKENS', 1000))
    
    # 解析 URL
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    
    # 构建请求数据
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
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
    response_data = response.read().decode('utf-8')
    conn.close()
    
    # 解析响应
    try:
        return json.loads(response_data)
    except json.JSONDecodeError:
        return {"error": "Invalid response from API", "response": response_data}

if __name__ == "__main__":
    # 加载环境变量
    env_vars = load_env()
    
    if not env_vars.get('TOKEN'):
        print("错误: 请在 .env 文件中设置 TOKEN")
        print("提示: 复制 .env.example 为 .env 并填写正确的 API 密钥")
    else:
        # 测试调用
        prompt = "你好，请介绍一下你自己"
        print(f"发送请求到: {env_vars.get('BASE_URL')}")
        print(f"使用模型: {env_vars.get('MODEL')}")
        print(f"提示词: {prompt}")
        print("\n正在请求...")
        
        result = call_llm(prompt, env_vars)
        
        print("\n响应结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))