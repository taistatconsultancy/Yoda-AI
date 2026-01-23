from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


class PromptNotFoundError(FileNotFoundError):
    pass


def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt template from app/ai/prompts/.

    prompt_name can be either:
    - "fourls_system.md"
    - "fourls_system" (we'll try common extensions)
    """
    candidates = []
    p = PROMPTS_DIR / prompt_name
    if p.suffix:
        candidates.append(p)
    else:
        candidates.extend([
            PROMPTS_DIR / f"{prompt_name}.md",
            PROMPTS_DIR / f"{prompt_name}.txt",
        ])

    for c in candidates:
        if c.exists():
            return c.read_text(encoding="utf-8")

    raise PromptNotFoundError(f"Prompt not found: {prompt_name} (looked in {PROMPTS_DIR})")


def render_prompt(template: str, variables: Dict[str, Any]) -> str:
    """
    Render a prompt template using Python format() with a variables dict.
    """
    return template.format(**variables)

