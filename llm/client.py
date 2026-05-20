import json

from openai import OpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from tools.smart_ops_tools import tools, execute_tool
from memory.chat_memory import get_history, save_history


client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)


SYSTEM_PROMPT = (
    "你是智能运维工单管理系统的 AI 助手。"
    "你可以帮助用户查询设备、查询工单、创建工单、自动派单、手动派单、维修人员接单、添加工单处理记录、完成工单、评价工单、取消工单。"
    "你也可以帮助用户查询巡检计划、巡检任务、开始巡检任务、提交巡检结果。"
    "你还可以查询通知、未读通知数量、标记通知已读、查询设备统计和工单统计。"
    "当用户需要查询真实业务数据或执行真实业务操作时，必须调用工具，不要编造系统中的业务数据。"
    "当用户询问系统规则、角色权限、设备状态含义、工单流程、巡检流程、Redis 或 RabbitMQ 使用场景时，"
    "应调用 search_knowledge_base 工具检索知识库，不要凭空回答。"
    "如果用户要求创建工单，在信息足够时必须调用 create_workorder 工具，不能只回复正在创建。"
    "如果缺少创建工单所需字段，例如设备ID、标题、故障描述、故障类型、位置、联系电话、优先级，请向用户追问。"
    "如果用户要求新增设备，缺少设备编号、设备名称、设备类型、区域、位置时，请向用户追问。"
    "如果用户要求完成工单，缺少工单ID或维修结果时，请向用户追问。"
    "如果用户要求提交巡检结果，缺少任务ID或巡检结果时，请向用户追问。"
    "对于删除、取消、禁用、全部已读等可能影响数据的操作，如果用户表达不明确，应先确认再执行。"
    "如果用户说“它”“这个设备”“刚才那个工单”“刚才那个任务”，请结合上下文理解。"
    "如果工具返回错误，请如实告诉用户失败原因。"
    "回答要简洁清晰，优先分点说明。"
)


def clean_history(history: list[dict]) -> list[dict]:
    """
    Redis Memory 只保留普通 user / assistant 对话。
    不保留 tool 消息，也不保留带 tool_calls 的 assistant 消息。
    否则下一轮请求 DeepSeek 时会出现：
    Messages with role 'tool' must be a response to a preceding message with 'tool_calls'
    """
    clean_messages = []

    for msg in history or []:
        role = msg.get("role")

        if role == "user":
            clean_messages.append({
                "role": "user",
                "content": msg.get("content", "")
            })

        elif role == "assistant":
            if msg.get("tool_calls"):
                continue

            content = msg.get("content")
            if content:
                clean_messages.append({
                    "role": "assistant",
                    "content": content
                })

        else:
            continue

    return clean_messages[-10:]


async def run_agent(
    user_message: str,
    token: str | None = None,
    session_id: str = "default",
) -> str:
    history = await get_history(session_id)
    history = clean_history(history)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        *history,
        {
            "role": "user",
            "content": user_message
        }
    ]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
    )

    assistant_message = response.choices[0].message

    messages.append(assistant_message)

    if not assistant_message.tool_calls:
        answer = assistant_message.content or ""

        memory_messages = [
            *history,
            {
                "role": "user",
                "content": user_message
            },
            {
                "role": "assistant",
                "content": answer
            }
        ]

        await save_history(session_id, clean_history(memory_messages))
        return answer

    for tool_call in assistant_message.tool_calls:
        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments

        tool_result = await execute_tool(
            tool_name=tool_name,
            arguments=arguments,
            token=token,
        )

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_result,
        })

    final_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
    )

    final_message = final_response.choices[0].message
    answer = final_message.content or ""

    memory_messages = [
        *history,
        {
            "role": "user",
            "content": user_message
        },
        {
            "role": "assistant",
            "content": answer
        }
    ]

    await save_history(session_id, clean_history(memory_messages))

    return answer