import os
from openai import OpenAI
import ollama


class OllamaProvider:

    def chat(self, messages, tools=None):
        model = os.getenv("OLLAMA_MODEL")
        host = os.getenv("OLLAMA_HOST")
        
        client = ollama.Client(host=host)

        return client.chat(
            model=model, messages=messages, tools=tools, options={"temperature": 0}
        )


class OpenAIProvider:

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def chat(self, messages, tools=None):
        model = os.getenv("OPENAI_MODEL")

        return self.client.chat.completions.create(
            model=model, messages=messages, tools=tools, temperature=0
        )


def get_llm_provider():
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "ollama":
        return OllamaProvider()

    if provider == "openai":
        return OpenAIProvider()

    raise ValueError(f"Unsupported LLM provider: {provider}")
