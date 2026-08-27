from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.ai_agent import main
from app.helper.schema import ChatRequest

from rich.console import Console

router = APIRouter()

console = Console()
@router.post("/chat")
def chat(payload: ChatRequest, x_access_token: Optional[str] = Header(default=None)):
    try:
        agent_response = main.run_agent(
            message=payload.message, history=None, token=x_access_token
        )

        if not agent_response:
            print("Agent Reposnse Error: ->>>> ", agent_response)

            raise HTTPException(status_code="500", detail="Empty response from agent")

        return {"success": True, "response": agent_response}
    except Exception as e:
        raise HTTPException(status_code="500", detail=f"Agent error: {str(e)}")
