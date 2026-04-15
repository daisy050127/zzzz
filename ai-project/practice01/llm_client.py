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
    
    return {
        "content": content,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "elapsed_time": elapsed_time,
        "tokens_per_second": tokens_per_second
    }

if __name__ == "__main__":
    # 加载环境变量
    env_vars = load_env()
    
    # 检查必要的环境变量
    if not env_vars.get('API_KEY'):
        print("请在 .env 文件中设置 API_KEY")
        exit(1)
    
    # 测试提示
    prompt = "请简要介绍一下人工智能的发展历史"
    
    print(f"发送请求到 LLM API...")
    print(f"模型: {env_vars.get('MODEL', 'gpt-3.5-turbo')}")
    print(f"基础 URL: {env_vars.get('BASE_URL', 'https://api.openai.com/v1')}")
    print(f"提示: {prompt}")
    print("=" * 80)
    
    try:
        # 调用 LLM
        result = call_llm(prompt, env_vars)
        
        # 输出结果
        print("回复内容:")
        print(result["content"])
        print("=" * 80)
        print(f"统计信息:")
        print(f"提示词 Token 数: {result['prompt_tokens']}")
        print(f"回复 Token 数: {result['completion_tokens']}")
        print(f"总 Token 数: {result['total_tokens']}")
        print(f"耗时: {result['elapsed_time']:.2f} 秒")
        print(f"Token/速度: {result['tokens_per_second']:.2f} tokens/秒")
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
