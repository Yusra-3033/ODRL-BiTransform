# === LLM Clients and Factory ===
# This module provides a unified interface to interact with different LLM providers
# such as OpenAI (GPT), Ollama (LLaMA), etc. It abstracts the underlying API calls
# and makes it easy to switch between providers by setting the LLM_PROVIDER environment variable.

# ollama_client.py
import os
import requests

class OllamaClient:
    def __init__(self):
        self.model = os.getenv("MODEL_NAME", "llama3.3:70b")
        self.temperature = float(os.getenv("TEMPERATURE", 0.4))
        self.api_url = os.getenv("OLLAMA_URL", "http://153.96.23.232/ollama/api/chat")

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        response = requests.post(self.api_url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("message", {}).get("content", "").strip()