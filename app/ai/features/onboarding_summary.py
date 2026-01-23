from __future__ import annotations

from typing import Any, Dict, Optional

from app.ai.openai_client import AIClient
from app.ai.prompt_loader import load_prompt, render_prompt
from app.ai.rag.chroma_store import ChromaStore
from app.ai.utils import hash_cache_key
from app.core.config import settings


def generate_onboarding_summary(
    *,
    ai: AIClient,
    workspace_id: int,
    source_text: str,
    endpoint_name: str,
    cache: bool = True,
) -> Dict[str, Any]:
    """
    Summarize onboarding/project documents using RAG chunks (instead of full document context).
    """
    model = "gpt-4o-mini"
    emb_model = getattr(settings, "AI_EMBEDDING_MODEL", "text-embedding-3-small") or "text-embedding-3-small"

    # NEW WORKFLOW: RAG comes from Chroma Cloud documents already indexed for this workspace.
    # We retrieve across ALL documents by filtering on workspace_id metadata.
    rag_used = True
    doc_hash = "workspace_scope"

    store = ChromaStore()
    query_text = "Summarize this project proposal: title, objective, problem, methodology, expected outcomes/impact, stakeholders/partners."
    retrieved = store.query(
        ai=ai,
        source="onboarding",
        query_text=query_text,
        embedding_model=emb_model,
        top_k=getattr(settings, "AI_RAG_TOP_K", 10),
        where_filter={"workspace_id": workspace_id},
    )
    context = "\n\n".join([c for c, _ in retrieved])
    if not context.strip():
        rag_used = False
        # Fallback: use a bounded excerpt of the last stored source_text (if present)
        context = (source_text or "")[:8000]

    system_tpl = load_prompt("onboarding_summary_system.md")
    user_tpl = load_prompt("onboarding_summary_user.md")
    user_prompt = render_prompt(user_tpl, {"rag_context": context})

    cache_key: Optional[str] = None
    if cache:
        cache_key = hash_cache_key(
            prompt=system_tpl + "\n---\n" + user_tpl,
            inputs={
                "workspace_id": workspace_id,
                "doc_hash": doc_hash,
                "top_k": getattr(settings, "AI_RAG_TOP_K", 10),
                "rag_used": rag_used,
            },
            model=model,
        )

    content, usage, cached = ai.chat_complete(
        endpoint_name=endpoint_name,
        model=model,
        messages=[
            {"role": "system", "content": system_tpl},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=400,
        cache_key=cache_key,
    )

    return {"summary": content, "usage": usage, "cached": cached, "model": model, "doc_hash": doc_hash, "rag_used": rag_used}

