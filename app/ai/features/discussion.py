from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.ai.openai_client import AIClient
from app.ai.prompt_loader import load_prompt, render_prompt
from app.core.config import settings


def facilitate_discussion_message(
    *,
    ai: AIClient,
    theme_title: str,
    theme_description: str,
    total_votes: int,
    history_messages: List[Dict[str, str]],
    endpoint_name: str,
) -> Tuple[str, Dict[str, Any]]:
    """
    history_messages: [{"role":"user"|"assistant","content":"..."}]
    """
    model = getattr(settings, "AI_MODEL", "gpt-4") or "gpt-4"
    system_tpl = load_prompt("discussion_facilitator_system.md")
    system_prompt = render_prompt(
        system_tpl,
        {"theme_title": theme_title, "theme_description": theme_description, "total_votes": total_votes},
    )

    content, usage, _cached = ai.chat_complete(
        endpoint_name=endpoint_name,
        model=model,
        messages=[{"role": "system", "content": system_prompt}, *history_messages],
        temperature=0.7,
        max_tokens=200,
        cache_key=None,
    )
    return content, usage


def answer_general_discussion_question(
    *,
    ai: AIClient,
    themes_context: str,
    da_context: str,
    user_message: str,
    endpoint_name: str,
) -> Tuple[str, Dict[str, Any]]:
    model = getattr(settings, "AI_MODEL", "gpt-4") or "gpt-4"
    system_tpl = load_prompt("discussion_general_system.md")
    system_prompt = render_prompt(system_tpl, {"themes_context": themes_context, "da_context": da_context})

    content, usage, _cached = ai.chat_complete(
        endpoint_name=endpoint_name,
        model=model,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
        temperature=0.7,
        max_tokens=300,
        cache_key=None,
    )
    return content, usage

