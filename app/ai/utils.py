from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional


def stable_json_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def hash_cache_key(*, prompt: str, inputs: Dict[str, Any], model: str, extra: Optional[Dict[str, Any]] = None) -> str:
    payload: Dict[str, Any] = {"prompt": prompt, "inputs": inputs, "model": model}
    if extra:
        payload["extra"] = extra
    raw = stable_json_dumps(payload).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

