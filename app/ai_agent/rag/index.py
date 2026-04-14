from app.ai_agent.db.index import client, COLLECTION_NAME, model
from qdrant_client.models import (
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
)
import json
import uuid
from .helper import update_last_indexed_line, get_last_indexed_line, clear_logs

LOG_FILE = "app/ai_agent/logs/log_agents.jsonl"
DB_PATH = "app/ai_agent/chroma_db"


def init_collection():
    collections = client.get_collections().collections

    exists = any(c.name == COLLECTION_NAME for c in collections)

    if not exists:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        print("Qdrant collection created")
    else:
        print("Collection ", COLLECTION_NAME, " is already present")


def index_logs(limit=100):
    points = []

    last_indexed = get_last_indexed_line()

    with open(LOG_FILE, "r") as f:
        lines = f.readlines()

    new_line = lines[last_indexed:]

    for i, line in enumerate(new_line, start=last_indexed):
        data = json.loads(line)

        content = f"{data.get('type')} : {data.get('data')}"
        embedding = model.encode(content).tolist()

        points.append(
            {
                "id": str(uuid.uuid4()),
                "vector": embedding,
                "payload": {"text": content, "type": data.get("type")},
            }
        )
    
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        
        update_last_indexed_line(len(lines))
        print(f"Indexed: {len(points)} new logs")
    else:
        print("No new logs to index")


def query_rag(query, k=3, log_type=None):
    query_embeddings = model.encode(query).tolist()

    search_kwargs = {
        "collection_name": COLLECTION_NAME,
        "query": query_embeddings,
        "limit": k,
    }

    if log_type:
        search_kwargs["query_filter"] = Filter(
            must=[FieldCondition(key="type", match=MatchValue(value=log_type))]
        )

    result = client.query_points(**search_kwargs)
    print(f"db result: {result}")
    return "\n".join([r.payload["text"] for r in result.points])
