from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional, Dict

from sqlalchemy import text

from app.database.database import engine

logger = logging.getLogger(__name__)


class AIResponseCache:
    """
    DB-backed cache keyed by a stable hash.

    - Uses CREATE TABLE IF NOT EXISTS at runtime (avoids Alembic coupling).
    - Keeps schema minimal: cache_key -> JSON payload.
    """

    _initialized: bool = False

    def _ensure_table(self) -> None:
        if self._initialized:
            return

        dialect = engine.dialect.name
        with engine.connect() as conn:
            if dialect == "postgresql":
                conn.execute(text(
                    """
                    CREATE TABLE IF NOT EXISTS ai_response_cache (
                        cache_key TEXT PRIMARY KEY,
                        endpoint_name TEXT NULL,
                        model TEXT NULL,
                        value_json JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    """
                ))
            else:
                conn.execute(text(
                    """
                    CREATE TABLE IF NOT EXISTS ai_response_cache (
                        cache_key TEXT PRIMARY KEY,
                        endpoint_name TEXT NULL,
                        model TEXT NULL,
                        value_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                    """
                ))
            conn.commit()

        self._initialized = True

    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        self._ensure_table()
        dialect = engine.dialect.name
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT value_json FROM ai_response_cache WHERE cache_key = :k"),
                {"k": cache_key},
            ).fetchone()
            if not row:
                return None
            raw = row[0]
            if dialect == "postgresql":
                # psycopg2 returns dict for JSONB in many configs; handle both.
                if isinstance(raw, (dict, list)):
                    return raw  # type: ignore[return-value]
                return json.loads(raw)
            return json.loads(raw)

    def set(self, cache_key: str, value: Dict[str, Any], *, endpoint_name: str, model: str) -> None:
        self._ensure_table()
        dialect = engine.dialect.name
        now = datetime.now(timezone.utc).isoformat()
        payload = value if dialect == "postgresql" else json.dumps(value)

        with engine.connect() as conn:
            if dialect == "postgresql":
                conn.execute(
                    text(
                        """
                        INSERT INTO ai_response_cache (cache_key, endpoint_name, model, value_json)
                        VALUES (:k, :e, :m, CAST(:v AS jsonb))
                        ON CONFLICT (cache_key) DO UPDATE SET
                          endpoint_name = EXCLUDED.endpoint_name,
                          model = EXCLUDED.model,
                          value_json = EXCLUDED.value_json,
                          created_at = NOW();
                        """
                    ),
                    {"k": cache_key, "e": endpoint_name, "m": model, "v": json.dumps(value)},
                )
            else:
                conn.execute(
                    text(
                        """
                        INSERT INTO ai_response_cache (cache_key, endpoint_name, model, value_json, created_at)
                        VALUES (:k, :e, :m, :v, :t)
                        ON CONFLICT(cache_key) DO UPDATE SET
                          endpoint_name=excluded.endpoint_name,
                          model=excluded.model,
                          value_json=excluded.value_json,
                          created_at=excluded.created_at;
                        """
                    ),
                    {"k": cache_key, "e": endpoint_name, "m": model, "v": payload, "t": now},
                )
            conn.commit()

