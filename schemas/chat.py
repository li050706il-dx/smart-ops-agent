from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    token: str | None = None
    session_id: str = "default"


class ChatResponse(BaseModel):
    answer: str