"""
Central AI layer.

This package owns:
- Prompt loading (app/ai/prompts/)
- All OpenAI calls (no direct OpenAI calls in routes)
- Response caching
- Token monitoring / guardrails
- RAG via ChromaDB (embeddings + retrieval)
"""

