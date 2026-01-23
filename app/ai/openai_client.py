from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

from app.core.config import settings
from app.ai.cache import AIResponseCache

logger = logging.getLogger(__name__)


class AIClient:
    """
    Central OpenAI client wrapper:
    - Token monitoring logs
    - Guardrails (warn on spikes / unusually large outputs)
    - Optional response caching via AIResponseCache
    """

    def __init__(self, cache: Optional[AIResponseCache] = None):
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self._client = OpenAI(api_key=api_key)
        self._cache = cache or AIResponseCache()

    def chat_complete(
        self,
        *,
        endpoint_name: str,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, Any]] = None,
        cache_key: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any], bool]:
        """
        Returns: (content, usage_dict, cached)
        """
        if cache_key:
            cached = self._cache.get(cache_key)
            if cached and isinstance(cached, dict) and "content" in cached:
                return str(cached["content"]), dict(cached.get("usage") or {}), True

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        resp = self._client.chat.completions.create(**kwargs)
        content = (resp.choices[0].message.content or "").strip()

        usage: Dict[str, Any] = {}
        if getattr(resp, "usage", None):
            usage = {
                "prompt_tokens": getattr(resp.usage, "prompt_tokens", None),
                "completion_tokens": getattr(resp.usage, "completion_tokens", None),
                "total_tokens": getattr(resp.usage, "total_tokens", None),
            }

        # Logging / guardrails
        logger.info(
            "ai.request",
            extra={
                "endpoint": endpoint_name,
                "model": model,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
            },
        )

        try:
            spike = getattr(settings, "AI_TOKEN_SPIKE_THRESHOLD", 8000)
            max_out = getattr(settings, "AI_MAX_OUTPUT_TOKENS", 2000)
            if usage.get("total_tokens") and usage["total_tokens"] > spike:
                logger.warning("ai.token_spike", extra={"endpoint": endpoint_name, "model": model, "total_tokens": usage["total_tokens"]})
            if usage.get("completion_tokens") and usage["completion_tokens"] > max_out:
                logger.warning("ai.output_too_large", extra={"endpoint": endpoint_name, "model": model, "completion_tokens": usage["completion_tokens"]})
        except Exception:
            # Never fail a request due to monitoring
            pass

        if cache_key:
            self._cache.set(cache_key, {"content": content, "usage": usage}, endpoint_name=endpoint_name, model=model)

        return content, usage, False

    def embed_texts(self, *, model: str, texts: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of texts.
        """
        resp = self._client.embeddings.create(model=model, input=texts)
        # resp.data is ordered to match input
        return [d.embedding for d in resp.data]

