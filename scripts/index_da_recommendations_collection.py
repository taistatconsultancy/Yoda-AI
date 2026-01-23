from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    root = _repo_root()
    # Allow `python scripts/...py` from repo root without installing as a package
    sys.path.insert(0, str(root))

    from app.ai.openai_client import AIClient
    from app.ai.rag.chroma_store import ChromaStore
    from app.core.config import settings

    parser = argparse.ArgumentParser(
        description="Index Disciplined Agile reference markdown into Chroma Cloud collection `da_recommendations`.",
    )
    parser.add_argument(
        "--file",
        default=str(root / "disciplined_agile_scrape.md"),
        help="Path to the Disciplined Agile markdown file.",
    )
    parser.add_argument(
        "--collection",
        default=getattr(settings, "CHROMA_DA_COLLECTION", "da_recommendations") or "da_recommendations",
        help="Chroma collection name to store DA embeddings.",
    )
    parser.add_argument(
        "--embedding-model",
        default=getattr(settings, "AI_EMBEDDING_MODEL", "text-embedding-3-small") or "text-embedding-3-small",
        help="OpenAI embedding model.",
    )
    parser.add_argument("--chunk-size", type=int, default=1500, help="Chunk size (characters).")
    parser.add_argument("--overlap", type=int, default=200, help="Chunk overlap (characters).")
    args = parser.parse_args()

    md_path = Path(args.file).expanduser().resolve()
    if not md_path.exists():
        raise FileNotFoundError(f"File not found: {md_path}")

    text = md_path.read_text(encoding="utf-8")

    ai = AIClient()
    store = ChromaStore(collection_name=str(args.collection))

    doc_id = md_path.name
    source = "disciplined_agile"

    doc_hash = store.upsert_text_document(
        ai=ai,
        source=source,
        doc_id=doc_id,
        text=text,
        embedding_model=str(args.embedding_model),
        chunk_size=int(args.chunk_size),
        overlap=int(args.overlap),
        extra_metadata={"kb": "disciplined_agile", "filename": doc_id},
    )

    count = store.count_chunks(where_filter={"source": source, "doc_id": doc_id, "doc_hash": doc_hash}, limit=5000)

    print("Indexed Disciplined Agile knowledge base.")
    print(f"- mode: {store.connection_mode()}")
    print(f"- chroma_database: {getattr(settings, 'CHROMA_DATABASE', None)}")
    print(f"- collection: {str(args.collection)}")
    print(f"- source: {source}")
    print(f"- doc_id: {doc_id}")
    print(f"- doc_hash: {doc_hash}")
    print(f"- chunks_counted: {count.get('count')} (limit_used={count.get('limit')})")
    if count.get("error"):
        print(f"- count_error: {count.get('error')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

