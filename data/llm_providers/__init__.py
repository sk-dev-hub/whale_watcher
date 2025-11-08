# data/llm_providers/__init__.py
from .grok import GrokProvider
from .openai import OpenAIProvider
from .local import LocalLLMProvider
from .mock import MockLLMProvider  # ← НОВЫЙ!

PROVIDERS = [
    GrokProvider,
    OpenAIProvider,
    LocalLLMProvider,
    MockLLMProvider  # ← Всегда в конце!
]

def get_llm_chain():
    available = []
    for P in PROVIDERS:
        p = P()
        if p.is_available():
            available.append(p)
    if not available:
        print("Все LLM недоступны")
    return available