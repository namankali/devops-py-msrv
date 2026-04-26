from fastapi import FastAPI
import threading
import os

from app.routes import chat

app = FastAPI(
    title="Ai-devops python microservice",
    version="1.0.0",
    description="Handles LLM calls",
)

app.include_router(chat.router, prefix="/ch", tags=["chats"])
