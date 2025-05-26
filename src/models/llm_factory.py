# === LLM Clients and Factory ===
# This module provides a unified interface to interact with different LLM providers
# such as OpenAI (GPT), Ollama (LLaMA), etc. It abstracts the underlying API calls
# and makes it easy to switch between providers by setting the LLM_PROVIDER environment variable.

# llm_factory.py
import os
from openai_client import OpenAIClient
from ollama_client import OllamaClient


def get_llm_client():
    #provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    if provider == "ollama":
        return OllamaClient()
    elif provider == "openai":
        return OpenAIClient()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")