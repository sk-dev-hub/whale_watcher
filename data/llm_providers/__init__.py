# data/llm_providers/__init__.py
"""
Фабрика для выбора LLM (ИИ-анализатора).
Пробует: Grok → OpenAI → Local → Mock.
Логирование через utils.logger.
"""
from typing import List
from .base import LLMProvider
from .grok import GrokProvider
from .openai import OpenAIProvider
from .local import LocalLLMProvider
from .mock import MockLLMProvider
from utils.logger import get_logger

# Логгер с именем модуля
log = get_logger()

# Порядок приоритета LLM
PROVIDERS = [
    GrokProvider,
    OpenAIProvider,
    LocalLLMProvider,
    MockLLMProvider  # Всегда в конце — fallback
]


def get_llm_chain() -> List[LLMProvider]:
    """
    Возвращает список доступных LLM в порядке приоритета.
    """
    chain = []
    for P in PROVIDERS:
        p = P()
        if p.is_available():
            chain.append(p)

    if not chain:
        log.warning("Все LLM провайдеры недоступны")
    else:
        log.info(f"Доступные LLM: {[p.__class__.__name__ for p in chain]}")

    return chain