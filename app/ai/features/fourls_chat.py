from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.ai.openai_client import AIClient
from app.ai.prompt_loader import load_prompt, render_prompt
from app.core.config import settings


def generate_fourls_reply(
    *,
    ai: AIClient,
    current_category: str,
    conversation_messages: List[Dict[str, str]],
    endpoint_name: str,
) -> Tuple[str, Dict[str, Any]]:
    """
    conversation_messages: list of {"role": "user"|"assistant", "content": "..."} (no system message)
    """
    model = getattr(settings, "AI_MODEL", "gpt-4") or "gpt-4"
    system_tpl = load_prompt("fourls_system.md")
    system_prompt = render_prompt(system_tpl, {"current_category_upper": (current_category or "").upper()})

    messages_for_ai: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    messages_for_ai.extend(conversation_messages)

    content, usage, _cached = ai.chat_complete(
        endpoint_name=endpoint_name,
        model=model,
        messages=messages_for_ai,
        temperature=0.3,
        max_tokens=220,
        cache_key=None,
    )

    return content, usage

