import os
from dotenv import load_dotenv
from ollama import Client
from openai import OpenAI

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_MODEL = "gpt-4.1-mini"
OLLAMA_MODEL = "qwen2.5:7b"
# OLLAMA_MODEL = "qwen3.5:4b"
# OLLAMA_MODEL = "qwen3.5:9b"

OpenAI()
ollama = Client(host="http://localhost:11434")
