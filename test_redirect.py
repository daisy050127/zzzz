import sys

# 重定向输出到文件
sys.stdout = open('output.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

print("开始执行测试...")

# 导入模块
import os
import time
import json
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse

print("模块导入成功")

# 读取 .env 文件
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), 'ai-project', '.env')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"')
    return env_vars

env_vars = load_env()
print(f"环境变量: {env_vars}")

# 解析 BASE_URL
url = urlparse(env_vars.get('BASE_URL', 'https://api.openai.com/v1'))
host = url.netloc
path = url.path or '/v1'
if not path.endswith('/'):
    path += '/'
if 'chat/completions' not in path:
    path += 'chat/completions'
print(f"URL 解析结果: scheme={url.scheme}, host={host}, path={path}")

# 构建请求数据
prompt = "请简要介绍一下人工智能的发展历史"
data = {
    "model": env_vars.get('MODEL', 'gpt-3.5-turbo'),
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.7
}
print(f"请求数据: {json.dumps(data, ensure_ascii=False)}")

# 构建请求头
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {env_vars.get('API_KEY', '')}"
}
print(f"请求头: {headers}")

print("测试完成")

# 关闭文件
sys.stdout.close()
