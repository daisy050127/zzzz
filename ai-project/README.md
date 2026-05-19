# AI 智能体开发学习项目

## 项目结构

```
.
├── practice01/
│   ├── llm_client.py         # 基础 LLM 客户端，使用标准 HTTP 库访问 LLM
│   └── chat_terminal.py      # 终端聊天界面，支持流式输出和历史记录
├── practice02/
│   ├── tool_client.py        # 工具调用终端，支持文件操作工具
│   └── test_tools.py         # 工具函数测试脚本
├── practice03/
│   ├── tool_client.py        # 扩展工具调用终端，添加网络访问功能
│   └── test_tools.py         # 工具函数测试脚本
├── practice04/
│   ├── tool_client.py        # 带历史记录压缩和关键信息提取的聊天终端
│   └── test_tools.py         # 工具函数测试脚本
├── practice05/
│   ├── tool_client.py        # 带AnythingLLM文档仓库查询功能的聊天终端
│   └── test_tools.py         # 工具函数测试脚本
├── practice06/
│   ├── tool_client.py        # 带技能调用功能的聊天终端
│   └── test_tools.py         # 工具函数测试脚本


## 代码功能说明

### 1. practice01/llm_client.py

**功能用途：**
- 读取项目根目录的 .env 文件，加载 LLM 配置信息
- 使用 Python 标准 HTTP 库（http.client）访问 OpenAI 兼容协议的 LLM API
- 支持发送聊天完成请求，获取模型响应
- 包含测试代码，可直接运行测试 API 调用

**教学目标：**
- 学习如何使用 Python 标准库读取环境配置文件
- 掌握 HTTP 客户端的基本使用方法
- 理解 OpenAI 兼容 API 的请求格式和响应处理
- 学习 JSON 数据的序列化和反序列化

### 2. practice01/chat_terminal.py

**功能用途：**
- 提供交互式终端聊天界面
- 支持用户输入聊天内容
- 支持流式输出模型响应
- 自动保存历史聊天记录并添加到上下文
- 支持 Ctrl+C 退出终端

**教学目标：**
- 学习如何构建交互式终端应用
- 掌握流式 API 调用的实现方法
- 理解聊天历史记录的管理和上下文维护
- 学习异常处理和用户中断处理

### 3. practice02/tool_client.py

**功能用途：**
- 基于 practice01 的聊天终端，添加工具调用功能
- 实现 5 个文件操作工具：
  1. `list_files()` - 列出目录下的文件及其属性
  2. `rename_file()` - 修改文件名字
  3. `delete_file()` - 删除文件
  4. `create_file()` - 新建文件并写入内容
  5. `read_file()` - 读取文件内容
- 支持工具调用的解析和执行
- 提供系统提示词，告知 LLM 可以使用的工具

**教学目标：**
- 学习如何扩展聊天终端，添加工具调用能力
- 理解工具函数的设计和实现
- 掌握工具调用的解析和执行逻辑
- 学习如何编写系统提示词，指导 LLM 使用工具

### 4. practice03/tool_client.py

**功能用途：**
- 基于 practice02 的工具调用终端，添加网络访问功能
- 新增 `fetch_webpage()` 工具，支持访问网页并返回内容
- 扩展系统提示词，添加新工具的说明
- 支持网页内容的获取和处理

**教学目标：**
- 学习如何扩展工具集，添加网络访问能力
- 掌握 HTTP 客户端访问外部网页的方法
- 理解网页内容的获取和处理
- 学习如何更新系统提示词，整合新工具

### 5. practice04/tool_client.py

**功能用途：**
- 基于 practice03 的工具调用终端，添加历史记录压缩和关键信息提取功能
- 当聊天超过5轮或上下文长度超过3k时，主动触发LLM执行聊天记录总结
- 对前70%左右的内容进行压缩，最后30%左右的内容保留原文
- 每五次聊天提取一次关键信息，按照5W规则（Who、What、When、Where、Why）提取
- 将提取的关键信息保存到 D:\chat-log\log.txt 文件中
- 新增 `search_chat_history()` 工具，支持搜索聊天历史记录
- 当用户发送以"/search"开头的消息或表达"查找聊天历史"的意思时，自动搜索聊天历史

**教学目标：**
- 学习如何设计和实现聊天历史记录的管理策略
- 掌握基于 LLM 的内容总结方法
- 理解上下文长度控制的重要性
- 学习如何实现智能的历史记录压缩算法
- 学习如何设计和实现基于 5W 规则的关键信息提取
- 学习如何进行文件系统操作和日志管理
- 理解如何实现聊天历史搜索功能

### 6. practice05/tool_client.py

**功能用途：**
- 基于 practice04 的工具调用终端，添加 AnythingLLM 文档仓库查询功能
- 新增 `anythingllm_query()` 工具，使用 subprocess 模块调用 curl 命令访问 AnythingLLM 的聊天 API 接口
- 支持中文编码处理
- 从 .env 文件中读取 ANYTHINGLLM_API_KEY 和 ANYTHINGLLM_WORKSPACE_SLUG 变量
- 当用户提到"文档仓库"、"文件仓库"、"仓库"时，自动触发 AnythingLLM 查询

**教学目标：**
- 学习如何使用 subprocess 模块调用外部命令
- 掌握 curl 命令的使用方法
- 理解 API 认证和授权机制
- 学习如何处理中文编码问题
- 理解如何集成第三方服务 API
- 学习如何扩展工具集，添加新的功能

### 7. practice06/tool_client.py

**功能用途：**
- 基于 practice05 的工具调用终端，添加技能调用功能
- 新增 `list_available_skills()` 工具，读取 D:\ttll\.agents\skills 目录下的所有一级子目录，提取每个技能的 name 和 description 字段
- 新增 `load_skill_content()` 工具，加载指定技能的 SKILL.md 文件内容
- 将技能列表以 JSON 格式通过系统提示词发送给 LLM
- 当用户需要撰写、修改、润色通知时，自动加载 notice 技能并按照技能内容执行

**教学目标：**
- 学习如何读取和解析文件系统中的技能文件
- 掌握 YAML front matter 的提取和解析方法
- 理解技能调用系统的设计和实现
- 学习如何将技能信息整合到系统提示词中
- 学习如何根据用户需求自动触发相应的技能

**测试要求：**
1. 模拟用户请求，不说部门，要求撰写五一节放假通知，应生成以"XX部通知"开头的内容
2. 模拟用户请求，表明部门是"销售部"，要求撰写五一节放假通知，应生成以"销售部通知"开头的内容

**技能文件：**
- `.agents/skills/notice/SKILL.md` - 通知撰写技能，包含通知格式和规则

**测试脚本：**
- `practice06/test_notice_skill.py` - 测试技能列表读取和技能内容加载
- `practice06/test_tool_call.py` - 测试工具调用执行过程


## 使用说明

1. **配置环境**
   - 复制 `.env.example` 为 `.env` 文件
   - 在 `.env` 文件中填写正确的 API 配置信息

2. **运行基础客户端**
   ```bash
   python practice01/llm_client.py
   ```

3. **运行终端聊天界面**
   ```bash
   python practice01/chat_terminal.py
   ```

4. **运行带文件操作工具的聊天终端**
   ```bash
   python practice02/tool_client.py
   ```

5. **运行带网络访问工具的聊天终端**
   ```bash
   python practice03/tool_client.py
   ```

6. **运行带历史记录压缩和关键信息提取的聊天终端**
   ```bash
   python practice04/tool_client.py
   ```

7. **运行带AnythingLLM文档仓库查询功能的聊天终端**
   ```bash
   python practice05/tool_client.py
   ```

8. **运行带技能调用功能的聊天终端**
   ```bash
   python practice06/tool_client.py
   ```

9. **运行基于practice04的带技能调用功能的聊天终端**
   ```bash
   python practice07/tool_client.py
   ```

10. **运行基于practice04的带技能调用功能的聊天终端（practice08）**
   ```bash
   python practice08/tool_client.py
   ```

## 环境变量配置

在 `.env` 文件中配置以下参数：

- `BASE_URL`: API 基础 URL（如 https://api.openai.com/v1）
- `MODEL`: 模型名称（如 gpt-3.5-turbo）
- `TOKEN`: API 密钥
- `TEMPERATURE`: 温度参数（0-1，越高越随机）
- `MAX_TOKENS`: 最大 tokens
- `ANYTHINGLLM_API_KEY`: AnythingLLM 的 API 密钥
- `ANYTHINGLLM_WORKSPACE_SLUG`: AnythingLLM 的工作空间标识符

## 教学重点

- **HTTP 客户端编程**：学习如何使用标准库发送 HTTP 请求和处理响应
- **环境配置管理**：学习如何使用 .env 文件管理配置信息
- **API 集成**：学习如何集成和使用 OpenAI 兼容的 LLM API
- **交互式应用开发**：学习如何构建终端交互式应用
- **流式输出处理**：学习如何实现流式 API 调用和实时输出
- **上下文管理**：学习如何维护和管理聊天历史记录
- **工具调用系统**：学习如何设计和实现工具调用机制
- **文件系统操作**：学习如何进行文件和目录的基本操作
- **网络访问**：学习如何使用 HTTP 客户端访问外部网页
- **系统提示词设计**：学习如何编写有效的系统提示词，指导 LLM 使用工具
- **工具扩展**：学习如何扩展工具集，添加新的功能
- **外部命令调用**：学习如何使用 subprocess 模块调用外部命令
- **第三方服务集成**：学习如何集成和使用第三方服务 API
- **API 认证**：理解 API 认证和授权机制
- **中文编码处理**：学习如何处理中文编码问题