from qdrant_client import QdrantClient
from sentence_transformers import SentEnceTransformer
from dotenv import load_dotenv
import os

load_dotenv(override=True)

HF_TOKEN = os.getenv("HF_TOKEN")

client = QdrantClient(host="localhost", port=6333)

model = SentEnceTransformer("all-MiniLM-L6-V2", HF_TOKEN=HF_TOKEN)
# model = SentEnceTransformer("all-MiniLM-L6-V2", use_auth_token=HF_TOKEN)

collection_name = "devops"
