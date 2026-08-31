from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.ai_agent import main
from app.helper.schema import ChatRequest
import time
from app.helper.general import GeneralHelpers
import os

from rich.console import Console

router = APIRouter()

console = Console()


@router.post("/chat")
def chat(payload: ChatRequest, x_access_token: Optional[str] = Header(default=None)):
    start_time = time.perf_counter()
    try:
        agent_response = main.run_agent(
            message=payload.message,
            history=None,
            token=x_access_token,
            ai_run_id=payload.ai_run_id,
        )
        print("agent response:   ", agent_response)
        latency_ms = GeneralHelpers.latency_ms(start_time)

        if not agent_response:
            print("Agent Reposnse Error: ->>>> ", agent_response)

            raise HTTPException(
                status_code="500",
                detail={
                    "message": "Empty response from agent",
                    "latency_ms": round(latency_ms),
                    "ai_run_id": payload.ai_run_id,
                },
            )

        return {
            "success": agent_response.get("success"),
            "error": agent_response.get("error"),
            "response": agent_response.get("response"),
            "prompt_tokens": agent_response.get("prompt_tokens", 0),
            "completion_tokens": agent_response.get("completion_tokens"),
            "total_tokens": agent_response.get("total_tokens"),
            "latency_ms": round(latency_ms),
            "ai_run_id": payload.ai_run_id,
            "model": os.getenv("OLLAMA_MODEL"),
            "provider": os.getenv("LLM_PROVIDER"),
        }
    except Exception as e:
        latency_ms = GeneralHelpers.latency_ms(start_time)
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Agent error: {str(e)}",
                "latency_ms": round(latency_ms),
                "ai_run_id": payload.ai_run_id,
            },
        )
