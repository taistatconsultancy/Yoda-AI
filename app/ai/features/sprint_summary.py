from __future__ import annotations

import json
from typing import Any, Dict, Optional

from app.ai.openai_client import AIClient
from app.ai.prompt_loader import load_prompt, render_prompt
from app.ai.utils import hash_cache_key
from app.core.config import settings


def generate_sprint_summary(
    *,
    ai: AIClient,
    data_summary: Dict[str, Any],
    endpoint_name: str,
    cache: bool = True,
) -> Dict[str, Any]:
    model = getattr(settings, "AI_MODEL", "gpt-4") or "gpt-4"

    prompt_tpl = load_prompt("sprint_summary_prompt.md")
    prompt = render_prompt(prompt_tpl, {"data_summary_json": json.dumps(data_summary, indent=2)})

    cache_key: Optional[str] = None
    if cache:
        cache_key = hash_cache_key(prompt=prompt_tpl, inputs={"data_summary": data_summary}, model=model)

    content, usage, cached = ai.chat_complete(
        endpoint_name=endpoint_name,
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert agile coach analyzing retrospectives."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=1000,
        response_format={"type": "json_object"},
        cache_key=cache_key,
    )

    try:
        summary_data = json.loads(content)
    except Exception:
        summary_data = {
            "summary": "Summary generation failed. Please review the retrospective data manually.",
            "achievements": [],
            "challenges": [],
            "recommendations": [],
        }

    return {"summary_data": summary_data, "usage": usage, "cached": cached, "model": model}

