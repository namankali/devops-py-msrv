from app.db.index import client, collection_name, model
from qdrant_client.models import (
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
    PointStruct,
    MatchAny,
)
import json
import uuid

VECTOR_SIZE = 384


def init_collection():
    collections = client.get_collections().collections

    exists = any(c.name == collection_name for c in collections)

    if not exists:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        print(f"Qdrant collection created: {collection_name}")
    else:
        print(f"Collection {collection_name} is already present")


def extract_failure_reason(logs: str) -> str:
    keywords = ["error", "failed", "exception", "traceback", "cannot", "not found"]

    lines = logs.splitlines()
    matched_lines = [line for line in lines if any(k in line.lower() for k in keywords)]

    if not matched_lines:
        return logs[-3000:]

    return "\n".join(matched_lines[-80:])


def store_build_failure(payload):
    init_collection()
    print("incoming payload ->>> ", payload.logs)
    failure_reason = extract_failure_reason(payload.logs)

    text = f"""
        Build failed in repository {payload.repo_name}

        Workflow: {payload.workflow_name}
        Job: {payload.job_name}
        Branch: {payload.branch}
        Commit: {payload.commit_sha}

        Failure Reason:
        {failure_reason}
    """
    print("failed_reason", text)
    vector = model.encode(text).tolist()

    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload={
            "type": "build_failure",
            "repo_id": payload.repo_id,
            "repo_name": payload.repo_name,
            "run_number": payload.run_number,
            "run_attempt": payload.run_attempt,
            "run_id": payload.run_id,
            "job_id": payload.job_id,
            "job_name": payload.job_name,
            "workflow_name": payload.workflow_name,
            "branch": payload.branch,
            "commit_sha": payload.commit_sha,
            "html_url": payload.html_url,
            "failure_reason": failure_reason,
            "text": text,
            "failure_date": payload.created_at[:10],
            "created_at": payload.created_at,
            "updated_at": payload.updated_at,
        },
    )

    client.upsert(collection_name=collection_name, points=[point])

    return {
        "stored": True,
        "repo_name": payload.repo_name,
        "run_id": payload.run_id,
        "job_id": payload.job_id,
    }


def search_build_failure(
    query: str,
    repo_name: str | None = None,
    failure_date: str | None = None,
    branch: str | None = None,
):

    query_vector = model.encode(query).tolist()
    # print("query __)))))) ", query, "query_vector ---)))) ", query_vector)
    must_filter = [FieldCondition(key="type", match=MatchValue(value="build_failure"))]

    if repo_name:
        must_filter.append(
            FieldCondition(key="repo_name", match=MatchValue(value=repo_name))
        )

    if failure_date:
        must_filter.append(
            FieldCondition(key="failure_date", match=MatchValue(value=failure_date))
        )

    if branch:
        must_filter.append(FieldCondition(key="branch", match=MatchValue(value=branch)))

    search_kwargs = {
        "collection_name": collection_name,
        "query": query_vector,
        "query_filter": Filter(must=must_filter),
        "limit": 5,
        "with_payload": True,
    }
    print("query kwargs", search_kwargs)

    results = client.query_points(**search_kwargs)
    # print(f"db result: {results}")

    return results.points


def get_failure_by_run_id(run_id: str | list[str]):
    if isinstance(run_id, str):
        run_ids = [run_id]
    else:
        run_ids = run_id

    results = client.scroll(
        collection_name=collection_name,
        scroll_filter=Filter(
            must=[
                FieldCondition(key="type", match=MatchValue(value="build_failure")),
                FieldCondition(key="run_id", match=MatchAny(any=run_ids)),
            ]
        ),
        with_payload=True,
        limit=100,
    )

    points, next_offset = results

    return points
