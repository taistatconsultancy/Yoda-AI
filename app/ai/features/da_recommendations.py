from __future__ import annotations

from typing import Any, Dict, Optional

from app.ai.openai_client import AIClient
from app.ai.prompt_loader import load_prompt, render_prompt
from app.ai.rag.chroma_store import ChromaStore
from app.ai.utils import hash_cache_key
from app.core.config import settings


def generate_da_recommendations(
    *,
    ai: AIClient,
    themes_text: str,
    endpoint_name: str,
    cache: bool = True,
) -> Dict[str, Any]:
    """
    Generate Disciplined Agile recommendations using RAG over the Chroma collection `da_recommendations`.

    Assumption: `scripts/index_da_recommendations_collection.py` (or equivalent) has already indexed the DA markdown
    into Chroma Cloud database "Novel" under collection `da_recommendations`.
    """
    model = getattr(settings, "AI_MODEL", "gpt-4") or "gpt-4"
    emb_model = getattr(settings, "AI_EMBEDDING_MODEL", "text-embedding-3-small") or "text-embedding-3-small"

    da_collection = getattr(settings, "CHROMA_DA_COLLECTION", "da_recommendations") or "da_recommendations"
    store = ChromaStore(collection_name=da_collection)

    # Query the pre-indexed DA knowledge base in Chroma
    retrieved = store.query(
        ai=ai,
        source="disciplined_agile",
        query_text=themes_text,
        embedding_model=emb_model,
        top_k=getattr(settings, "AI_RAG_TOP_K", 6),
        where_filter={"kb": "disciplined_agile"},
    )
    context = "\n\n".join([c for c, _ in retrieved])

    prompt_tpl = load_prompt("da_recommendations_prompt.md")
    prompt = render_prompt(prompt_tpl, {"themes_text": themes_text, "rag_context": context})

    cache_key: Optional[str] = None
    if cache:
        kb_count = store.count_chunks(where_filter={"source": "disciplined_agile", "kb": "disciplined_agile"}, limit=300).get("count")
        cache_key = hash_cache_key(
            prompt=prompt_tpl,
            inputs={
                "themes_text": themes_text,
                "collection": da_collection,
                "kb_count": kb_count,
                "top_k": getattr(settings, "AI_RAG_TOP_K", 6),
            },
            model=model,
        )

    content, usage, cached = ai.chat_complete(
        endpoint_name=endpoint_name,
        model=model,
        messages=[
            {"role": "system", "content": "You are a Disciplined Agile expert providing actionable recommendations."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
        max_tokens=1500,
        cache_key=cache_key,
    )

    return {"content": content, "usage": usage, "cached": cached, "model": model}

