# === LLM Clients and Factory ===
# This module provides a unified interface to interact with different LLM providers
# such as OpenAI (GPT), Ollama (LLaMA), etc. It abstracts the underlying API calls
# and makes it easy to switch between providers by setting the LLM_PROVIDER environment variable.

# openai_client.py
import os
import openai
import backoff
from openai.error import RateLimitError, Timeout, APIError

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.model = os.getenv("MODEL_NAME", "gpt-4-turbo-preview")
        self.temperature = float(os.getenv("TEMPERATURE", 0.5))
        self.max_tokens = int(os.getenv("MAX_TOKENS", 1024))

    @backoff.on_exception(
        backoff.expo,
        (RateLimitError, Timeout, APIError),
        max_tries=5,
        jitter=None
    )
    def generate(self, prompt: str) -> str:
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content.strip()