from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv(override=True)

HF_TOKEN = os.getenv("HF_TOKEN")

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = os.getenv("QDRANT_PORT")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-V2")

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# model = SentenceTransformer("all-MiniLM-L6-V2", HF_TOKEN=HF_TOKEN)
model = SentenceTransformer(EMBEDDING_MODEL, use_auth_token=HF_TOKEN)

collection_name = "devops"
