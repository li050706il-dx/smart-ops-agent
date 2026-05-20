# Smart Ops Agent

智能运维工单管理系统 Python AI Agent 服务。

本项目基于 FastAPI 构建，接入 DeepSeek 大模型，支持 Tool Calling、Redis 多轮记忆和 RAG 知识库检索。Agent 可以通过工具函数调用 Java 后端业务接口，实现自然语言操作真实业务数据。

## 技术栈

- Python
- FastAPI
- Uvicorn
- OpenAI SDK compatible API
- DeepSeek Chat
- Tool Calling
- Redis Memory
- ChromaDB
- RAG
- httpx
- Pydantic

## 核心功能

### AI 对话接口

提供 AI 对话接口：

```text
POST /agent/chat
```

支持用户通过自然语言完成：

- 查询设备
- 新增设备
- 修改设备状态
- 查询工单
- 创建工单
- 自动派单
- 手动派单
- 维修人员接单
- 添加工单处理记录
- 完成工单
- 评价工单
- 取消工单
- 查询巡检计划
- 创建巡检计划
- 开始巡检任务
- 提交巡检结果
- 查询通知
- 标记通知已读
- 查询系统规则

### Tool Calling

Agent 根据用户意图自动选择工具，并调用 Java 后端真实业务接口。

常见工具包括：

```text
get_device_detail
search_devices
add_device
update_device_status
create_workorder
search_workorders
auto_assign_workorder
assign_workorder
finish_workorder
create_inspection_plan
submit_inspection_task
get_unread_notice_count
search_knowledge_base
```

### Redis Memory

使用 Redis 保存多轮上下文，使 AI 能理解：

```text
刚才那个设备
这个工单
继续处理
它的状态
```

Redis Key 示例：

```text
smartops:agent:memory:web_user_1
```

Memory 只保存普通 user / assistant 对话，不保存 tool 调用过程，避免出现大模型消息格式错误。

### RAG 知识库

使用 ChromaDB 构建本地知识库，用于回答系统规则类问题。

适合检索：

- 系统角色权限
- 设备状态含义
- 工单流转流程
- 巡检流程
- Redis 使用场景
- RabbitMQ 使用场景
- AI Agent 说明

## 项目结构

```text
smart-ops-agent
├── clients
│   └── smart_ops_api.py       调用 Java 后端接口
├── llm
│   └── client.py              大模型调用与 Agent 主流程
├── memory
│   └── chat_memory.py         Redis 多轮记忆
├── rag
│   ├── docs                   知识库文档
│   ├── ingest.py              文档入库
│   └── retriever.py           知识库检索
├── routers
│   └── agent.py               FastAPI 路由
├── schemas
│   └── chat.py                请求响应模型
├── tools
│   └── smart_ops_tools.py     Tool Calling 工具定义和执行
├── config.py
├── main.py
├── requirements.txt
└── .env.example
```

## 环境变量

复制 `.env.example` 为 `.env`：

```bash
copy .env.example .env
```

`.env.example` 示例：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

SMART_OPS_BASE_URL=http://localhost:8080

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
CHAT_MEMORY_TTL_SECONDS=86400
```

注意：`.env` 不要提交到 GitHub。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动服务

```bash
uvicorn main:app --reload --port 8000
```

访问接口文档：

```text
http://localhost:8000/docs
```

## 知识库入库

如果修改了 `rag/docs` 下的知识文档，需要重新执行：

```bash
python rag/ingest.py
```

然后重启 Agent 服务。

## 请求示例

```json
{
  "message": "查询设备1",
  "token": "your_java_token",
  "session_id": "web_user_1"
}
```

## 测试提示词

查询设备：

```text
查询设备1的详细信息
```

创建工单：

```text
帮我创建一个工单，设备ID是1，标题是空调不制冷，描述是教室空调没有冷风，故障类型是空调故障，位置是教学楼A区302，联系电话是13800000000，优先级是3
```

查询系统规则：

```text
巡检异常后系统会做什么？
```

查询通知：

```text
帮我查询未读通知数量
```

## 调用链路

```text
用户
  -> Vue 前端 AI 对话框
  -> Java 后端 /ai/chat
  -> Python Agent /agent/chat
  -> DeepSeek
  -> Tool Calling
  -> Java 业务接口
  -> 返回最终回答
```

## 启动依赖

启动 Agent 前请确保以下服务可用：

- Java 后端 smart-ops-system
- Redis
- DeepSeek API Key

完整项目启动顺序：

```text
1. 启动 MySQL、Redis、RabbitMQ
2. 启动 Java 后端 smart-ops-system，端口 8080
3. 启动 Python Agent smart-ops-agent，端口 8000
4. 启动 Vue 前端 smart-ops-web，端口 5173
```

## 注意事项

不要提交以下文件或目录：

```text
.venv/
.env
__pycache__/
chroma_db/
.idea/
*.pyc
logs/
```

如果运行在 Docker 中，不能使用 `localhost` 访问其他容器，需要使用 Docker Compose 服务名，例如：

```text
smart-ops-system
redis
```
