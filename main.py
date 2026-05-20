from fastapi import FastAPI
from routers.agent import router as agent_router

app = FastAPI(
    title="Smart Ops Agent",
    description="智能运维工单管理系统 AI Agent 服务",
    version="0.1.0",
)

app.include_router(agent_router)


@app.get("/")
def root():
    return {
        "message": "Smart Ops Agent is running"
    }