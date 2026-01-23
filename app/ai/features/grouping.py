from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from app.ai.openai_client import AIClient
from app.ai.prompt_loader import load_prompt, render_prompt
from app.ai.utils import hash_cache_key
from app.core.config import settings


_ALLOWED_CATEGORIES = {"liked", "learned", "lacked", "longed_for"}


def _normalize_primary_category(v: Any) -> str:
    s = (str(v or "")).strip().lower()
    if s in _ALLOWED_CATEGORIES:
        return s
    # common variants
    if s in {"longedfor", "longed", "longed_for_", "longedfor_"}:
        return "longed_for"
    return "liked"


def _trim_to_max_words(text: str, max_words: int) -> str:
    words = [w for w in (text or "").strip().split() if w]
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words])


def _first_n_sentences(text: str, n: int = 2) -> str:
    s = (text or "").strip()
    if not s:
        return ""
    # naive sentence split, good enough for short summaries
    parts = re.split(r"(?<=[.!?])\s+", s)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return s
    return " ".join(parts[:n])


def _normalize_themes(themes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen_titles = set()

    for t in themes or []:
        if not isinstance(t, dict):
            continue

        title = str(t.get("title") or "").strip()
        desc = str(t.get("description") or "").strip()
        primary_category = _normalize_primary_category(t.get("primary_category"))

        # Title cleanup
        title = title.strip().strip("-").strip()
        title = title.rstrip(".:;,-–— ").strip()
        title = _trim_to_max_words(title, 6)
        if not title:
            continue

        # De-dupe by case-insensitive title
        key = title.lower()
        if key in seen_titles:
            continue
        seen_titles.add(key)

        # Description cleanup: keep 1–2 sentences
        desc = _first_n_sentences(desc, 2)
        if not desc:
            desc = "Theme summarized from team responses."

        # Normalize contributors
        contributors_raw = t.get("contributors") or []
        contributors: List[str] = []
        if isinstance(contributors_raw, list):
            for c in contributors_raw:
                cs = str(c or "").strip()
                if cs and cs not in contributors:
                    contributors.append(cs)

        # Normalize response_ids (optional but preferred)
        response_ids_raw = t.get("response_ids") or []
        response_ids: List[int] = []
        if isinstance(response_ids_raw, list):
            for rid in response_ids_raw:
                try:
                    response_ids.append(int(rid))
                except Exception:
                    continue

        out.append(
            {
                "title": title,
                "description": desc,
                "primary_category": primary_category,
                "contributors": contributors,
                "response_ids": response_ids,
            }
        )

    return out


def generate_theme_grouping(
    *,
    ai: AIClient,
    responses_text: List[Dict[str, Any]],
    endpoint_name: str,
    cache: bool = True,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], bool]:
    """
    Generate grouping JSON (themes). Returns (themes, usage, cached).
    """
    model = getattr(settings, "AI_MODEL", "gpt-4") or "gpt-4"
    prompt_tpl = load_prompt("grouping_prompt.md")
    prompt = render_prompt(prompt_tpl, {"responses_json": json.dumps(responses_text, indent=2)})

    cache_key: Optional[str] = None
    if cache:
        cache_key = hash_cache_key(
            prompt=prompt_tpl,
            inputs={"responses_text": responses_text},
            model=model,
        )

    content, usage, cached = ai.chat_complete(
        endpoint_name=endpoint_name,
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert at analyzing team retrospectives and identifying patterns and themes. Always respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=2000,
        response_format={"type": "json_object"},
        cache_key=cache_key,
    )

    # Strip markdown fences if the model returns them
    ai_response = content.strip()
    if ai_response.startswith("```"):
        lines = ai_response.split("\n")
        ai_response = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        ai_response = ai_response.replace("```json", "").replace("```", "").strip()

    parsed = json.loads(ai_response)
    themes = parsed if isinstance(parsed, list) else (parsed.get("themes", []) if isinstance(parsed, dict) else [])
    if not isinstance(themes, list):
        themes = []

    themes = _normalize_themes(themes)

    return themes, usage, cached

