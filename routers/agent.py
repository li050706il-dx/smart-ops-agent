from fastapi import APIRouter

from schemas.chat import ChatRequest, ChatResponse
from llm.client import run_agent

router = APIRouter(prefix="/agent", tags=["AI Agent"])


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    answer = await run_agent(
        user_message=req.message,
        token=req.token,
        session_id=req.session_id,
    )

    return ChatResponse(answer=answer)