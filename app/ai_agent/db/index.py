from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

LOG_FILE = "app/ai_agent/logs/agent_logs.jsonl"

client = QdrantClient(host="localhost", port=6333)

model = SentenceTransformer("all-MiniLM-L6-v2", use_auth_token=HF_TOKEN)

COLLECTION_NAME = "agents_logs"
    
