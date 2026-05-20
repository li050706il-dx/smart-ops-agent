import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
SMART_OPS_BASE_URL = os.getenv("SMART_OPS_BASE_URL", "http://localhost:8080")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

_raw_redis_password = os.getenv("REDIS_PASSWORD", "").strip()
REDIS_PASSWORD = _raw_redis_password if _raw_redis_password else None

CHAT_MEMORY_TTL_SECONDS = int(os.getenv("CHAT_MEMORY_TTL_SECONDS", "86400"))