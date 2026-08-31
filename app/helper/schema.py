from pydantic import BaseModel, Field
from typing import Dict, List, Any


class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = []
    ai_run_id: int


class BuildFailureRequest(BaseModel):
    repo_id: Any
    repo_name: Any
    run_id: Any
    run_number: int
    run_attempt: int
    job_id: Any
    job_name: Any
    workflow_name: Any
    branch: Any
    commit_sha: Any
    html_url: Any
    logs: Any
    created_at: Any
    updated_at: Any


class FailureData(BaseModel):
    run_id: str
    run_number: int
    status: str
    conclusion: str
    run_attempt: str
    workflow_run_name: str
    repo_name: str
    branch: str
    commit_sha: str
    display_title: str
    html_url: str
    created_at: str
    updated_at: str
    probable_fix: str | None = None


class FailureReason(FailureData):
    failure_reason: str
