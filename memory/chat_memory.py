import json
from typing import Any

import redis.asyncio as redis

from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_PASSWORD,
    CHAT_MEMORY_TTL_SECONDS,
)


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
)


def build_memory_key(session_id: str) -> str:
    return f"smartops:agent:memory:{session_id}"


async def get_history(session_id: str) -> list[dict[str, Any]]:
    """
    从 Redis 获取某个会话的历史消息。
    """
    key = build_memory_key(session_id)

    raw = await redis_client.get(key)

    if not raw:
        return []

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


async def save_history(
    session_id: str,
    messages: list[dict[str, Any]],
    max_messages: int = 30,
) -> None:
    """
    保存某个会话的历史消息到 Redis。
    只保留最近 max_messages 条，避免上下文无限增长。
    """
    key = build_memory_key(session_id)

    recent_messages = messages[-max_messages:]

    await redis_client.set(
        key,
        json.dumps(recent_messages, ensure_ascii=False),
        ex=CHAT_MEMORY_TTL_SECONDS,
    )


async def clear_history(session_id: str) -> None:
    """
    清空某个会话的历史。
    """
    key = build_memory_key(session_id)
    await redis_client.delete(key)