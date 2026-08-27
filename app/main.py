from fastapi import FastAPI

from app.routes import chat, rag

app = FastAPI(
    title="AI DevOps Python Microservice",
    version="1.0.0",
    description="Handles LLM calls",
)

app.include_router(chat.router, prefix="/ch", tags=["Chats"])
app.include_router(rag.router, prefix="/rag", tags=["RAG"])


@app.get("/")
async def root():
    return {
        "success": True,
        "service": "AI DevOps Python Microservice",
        "version": "1.0.0",
    }