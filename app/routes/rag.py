from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.helper.schema import BuildFailureRequest
from app.rag.index import store_build_failure
import traceback

router = APIRouter()


@router.post("/ingest-build-failure")
def failure_build_data(
    payload: BuildFailureRequest, x_access_token: Optional[str] = Header(default=None)
):
    try:
        result = store_build_failure(payload=payload)

        return {"success": True, "response": result}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
