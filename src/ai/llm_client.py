import json
from typing import Any

import ollama

from src.config import settings
from src.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name or getattr(settings, "OLLAMA_MODEL", "llama3")

    def generate_json(self, prompt: str) -> dict[str, Any] | None:
        messages = [{"role": "user", "content": prompt}]

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                format="json",
            )
        except Exception:
            logger.exception("LLM request failed")
            return None

        content = response.get("message", {}).get("content")
        if isinstance(content, dict):
            return content
        if isinstance(content, str):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logger.error("LLM returned invalid JSON")
                return None

        logger.error("LLM response missing JSON content")
        return None
