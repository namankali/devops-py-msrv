import os
from dotenv import load_dotenv
from ollama import Client
from openai import OpenAI

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# print(f"openai api key: {OPENAI_API_KEY}")

OPENAI_MODEL = "gpt-4.1-mini"
OLLAMA_MODEL = "qwen2.5:7b"
# OLLAMA_MODEL = "qwen2.5:3b"

openai = OpenAI()
ollama = Client(host="http://localhost:11434")
