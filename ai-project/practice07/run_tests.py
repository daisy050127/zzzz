"""运行链式工具调用测试"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tool_client import test_chained_calls

if __name__ == "__main__":
    test_chained_calls()