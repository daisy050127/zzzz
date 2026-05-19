# Practice07 - 链式工具调用（Chained Tool Calls）

## 项目简介

本项目在 practice06 的基础上，实现了**链式工具调用（Chained Tool Calls）**功能，即前一个工具的输出可以作为后一个工具的输入参数，让 LLM 能够根据中间结果自主决定下一步工具调用。

## 核心功能

### 1. 链式调用上下文管理器（ChainedCallContext）

用于在多个工具调用之间传递数据和状态：
- 记录每一步的调用和结果
- 存储中间变量供后续步骤使用
- 设置最大迭代次数，防止无限循环

### 2. 链式调用执行函数（execute_chained_tool_call）

实现链式工具调用的完整流程：
1. 初始化消息历史，包含 system prompt
2. 循环最多 `max_iterations` 次：
   - 构建分析提示词（包含用户请求和已执行的步骤历史）
   - 调用 LLM 决定下一步操作
   - 解析 LLM 响应（支持 JSON 格式）
   - 如果任务完成，返回最终回答
   - 如果需继续调用，执行工具并记录到上下文
   - 将结果添加到消息历史，继续下一轮

### 3. 分析提示词构建函数（build_analysis_prompt）

提示词包含：
- 用户原始请求
- 已执行的工具调用历史（工具名、参数、结果）
- 决策规则说明
- JSON 输出格式要求

## 输出格式要求

LLM 需要按照以下 JSON 格式返回决策：

### 完成任务时
```json
{"done": true, "answer": "最终回答内容"}
```

### 继续调用工具时
```json
{"done": false, "tool_call": {"name": "工具名称", "arguments": {"参数名": "参数值"}}}
```

## 系统提示词更新

在 system prompt 中明确链式调用的规则：
- 说明工具调用的顺序依赖关系
- 指导 LLM 如何根据中间结果决定后续操作
- 提供链式调用的示例
- 说明上下文变量的使用方式

## 可用工具列表

| 工具名称 | 功能描述 | 参数 |
|---------|---------|------|
| `list_files` | 列出目录下的文件和文件夹 | `directory` - 目录路径 |
| `rename_file` | 修改文件名 | `directory`, `old_name`, `new_name` |
| `delete_file` | 删除文件 | `directory`, `file_name` |
| `create_file` | 创建文件 | `directory`, `file_name`, `content` |
| `read_file` | 读取文件内容 | `directory`, `file_name` |
| `fetch_webpage` | 访问网页 | `url` - 网页地址 |
| `search_chat_history` | 搜索聊天历史 | `query` - 搜索关键词 |
| `anythingllm_query` | 查询文档仓库 | `message` - 查询消息 |
| `load_skill_content` | 加载技能内容 | `skill_name` - 技能名称 |

## 测试示例

### 测试1：文件搜索链式调用
```
用户请求："请查找 practice06 目录下所有包含'def'关键词的文件，并总结这些文件的主要内容"
```

### 测试2：技能查询链式调用
```
用户请求："我想了解 notice 技能的详细规则"
```

### 测试3：网页处理链式调用
```
用户请求："访问 https://www.example.com 并总结页面内容，保存到 practice07/summary.txt"
```

## 运行方式

```bash
cd practice07
python tool_client.py
```

### 命令说明
- 输入 `exit` 退出程序
- 输入 `test` 运行预设的三个测试用例
- 输入其他内容作为用户请求，程序将自动进行链式工具调用

## 环境配置

在项目根目录创建 `.env` 文件，配置以下参数：

```env
TOKEN=your_api_key_here
BASE_URL=https://api.openai.com/v1
MODEL=gpt-3.5-turbo
TEMPERATURE=0.7
MAX_TOKENS=1000
ANYTHINGLLM_API_KEY=your_anythingllm_key
ANYTHINGLLM_WORKSPACE_SLUG=your_workspace
```

## 技术特点

1. **自动决策**：LLM 根据对话历史自动决定是否调用工具以及调用哪个工具
2. **链式传递**：前一个工具的输出可以作为后一个工具的输入
3. **状态管理**：通过上下文管理器维护调用状态和中间变量
4. **安全机制**：设置最大迭代次数，防止无限循环
5. **灵活扩展**：支持添加新的工具函数

## 教学目标

通过本项目学习：
- 如何实现多步骤工具调用的协调与管理
- 如何让 LLM 根据中间结果自主决策
- 如何设计上下文管理器来传递状态
- 如何构建有效的提示词引导 LLM 行为
- 如何处理复杂的多步骤任务流程
