from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.ai.openai_client import AIClient
from app.ai.rag.chunking import chunk_text
from app.ai.utils import hash_text

logger = logging.getLogger(__name__)


class ChromaStore:
    """
    Minimal ChromaDB wrapper:
    - Upsert chunked documents with OpenAI embeddings
    - Query top-k relevant chunks by embedding similarity

    Storage strategy:
    - Default: PersistentClient(path=CHROMA_PERSIST_DIR)
    - Optional: HttpClient(host/port) if CHROMA_HOST is configured
    """

    def __init__(self, *, collection_name: Optional[str] = None):
        try:
            import chromadb  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError("chromadb is not installed. Ensure requirements.txt includes chromadb.") from e

        self._chromadb = chromadb
        default_collection = getattr(settings, "CHROMA_COLLECTION", "thematic_embeddings") or "thematic_embeddings"
        self._collection_name = collection_name or default_collection

        host = getattr(settings, "CHROMA_HOST", None)
        port = getattr(settings, "CHROMA_PORT", None)
        persist_dir = getattr(settings, "CHROMA_PERSIST_DIR", "./.chroma")

        # Prefer Chroma Cloud if credentials are present.
        force_cloud = bool(getattr(settings, "CHROMA_FORCE_CLOUD", False))
        api_key = getattr(settings, "CHROMA_API_KEY", None)
        tenant = getattr(settings, "CHROMA_TENANT", None)
        # Chroma Cloud database name (optional). If set incorrectly, Chroma will raise a database mismatch error.
        # Only pass it when explicitly provided to avoid accidental mismatches.
        database = getattr(settings, "CHROMA_DATABASE", None)

        if force_cloud and not (api_key and tenant):
            raise RuntimeError(
                "CHROMA_FORCE_CLOUD=true but Chroma Cloud credentials are missing. "
                "Set CHROMA_API_KEY and CHROMA_TENANT."
            )

        if api_key and tenant:
            # Chroma Cloud path: try CloudClient first; otherwise fall back to HttpClient.
            cloud_client = getattr(chromadb, "CloudClient", None)
            if cloud_client is not None:
                # CloudClient signatures have varied; try the most specific first.
                try:
                    if database:
                        self._client = cloud_client(api_key=api_key, tenant=tenant, database=database)
                    else:
                        self._client = cloud_client(api_key=api_key, tenant=tenant)
                except TypeError:
                    # Fallback for older/newer signatures
                    self._client = cloud_client(api_key=api_key, tenant=tenant)
            else:
                if not host:
                    raise RuntimeError(
                        "Chroma Cloud credentials provided but CHROMA_HOST is not set and chromadb.CloudClient is unavailable. "
                        "Set CHROMA_HOST/CHROMA_PORT (and CHROMA_SSL) for HttpClient."
                    )
                headers = {}
                # Default to Bearer auth; override via CHROMA_HEADERS_JSON if needed.
                headers["Authorization"] = f"Bearer {api_key}"
                headers_json = getattr(settings, "CHROMA_HEADERS_JSON", None)
                if headers_json:
                    import json
                    try:
                        extra = json.loads(headers_json)
                        if isinstance(extra, dict):
                            headers.update({str(k): str(v) for k, v in extra.items()})
                    except Exception:
                        pass
                ssl = bool(getattr(settings, "CHROMA_SSL", True))
                self._client = chromadb.HttpClient(host=host, port=port or 443, ssl=ssl, headers=headers)
        elif host and not force_cloud:
            # Self-hosted Chroma via HTTP.
            ssl = bool(getattr(settings, "CHROMA_SSL", True))
            headers = {}
            headers_json = getattr(settings, "CHROMA_HEADERS_JSON", None)
            if headers_json:
                import json
                try:
                    extra = json.loads(headers_json)
                    if isinstance(extra, dict):
                        headers.update({str(k): str(v) for k, v in extra.items()})
                except Exception:
                    pass
            self._client = chromadb.HttpClient(host=host, port=port or 8000, ssl=ssl, headers=headers or None)
        else:
            # Local persistence (dev only)
            if force_cloud:
                raise RuntimeError("CHROMA_FORCE_CLOUD=true but falling back to local persistence is not allowed.")
            self._client = chromadb.PersistentClient(path=persist_dir)

        self._collection = self._client.get_or_create_collection(name=self._collection_name)

    def connection_mode(self) -> str:
        """
        Best-effort string describing which connection mode is active.
        """
        api_key = getattr(settings, "CHROMA_API_KEY", None)
        tenant = getattr(settings, "CHROMA_TENANT", None)
        database = getattr(settings, "CHROMA_DATABASE", None)
        host = getattr(settings, "CHROMA_HOST", None)
        if api_key and tenant and database:
            # If CloudClient exists, we used it; otherwise we used HttpClient fallback.
            cloud_client = getattr(self._chromadb, "CloudClient", None)
            return "cloudclient" if cloud_client is not None else "cloud_http"
        if host:
            return "http"
        return "local"

    def _is_indexed(self, *, source: str, doc_id: str, doc_hash: str) -> bool:
        """
        Best-effort check to avoid re-embedding the same document on every request.
        """
        try:
            where = self._build_where({"source": source, "doc_id": doc_id, "doc_hash": doc_hash})
            # Chroma v2 requires operator syntax in where; ids are always returned.
            res = self._collection.get(where=where, limit=1)
            ids = res.get("ids") or []
            return bool(ids)
        except Exception:
            return False

    def get_index_stats(self, *, source: str, doc_id: str, text: str) -> Dict[str, Any]:
        """
        Return index stats for a given source/doc_id + current text hash.
        """
        doc_hash = hash_text(text or "")
        try:
            where = self._build_where({"source": source, "doc_id": doc_id, "doc_hash": doc_hash})
            res = self._collection.get(where=where, limit=5)
            ids = res.get("ids") or []
            return {
                "mode": self.connection_mode(),
                "collection": self._collection_name,
                "source": source,
                "doc_id": doc_id,
                "doc_hash": doc_hash,
                "indexed": bool(ids),
                "chunk_count": len(ids),
            }
        except Exception as e:
            return {
                "mode": self.connection_mode(),
                "collection": self._collection_name,
                "source": source,
                "doc_id": doc_id,
                "doc_hash": doc_hash,
                "indexed": False,
                "chunk_count": 0,
                "error": str(e),
            }

    def _build_where(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chroma Cloud (v2) requires operator syntax in `where`:
          - single condition: {"field": {"$eq": value}}
          - multiple: {"$and": [ {"a":{"$eq":1}}, {"b":{"$eq":"x"}} ]}

        Using this format also works with recent local chromadb versions.
        """
        conds: List[Dict[str, Any]] = []
        for k, v in (filters or {}).items():
            if v is None:
                continue
            conds.append({k: {"$eq": v}})
        if not conds:
            return {}
        if len(conds) == 1:
            return conds[0]
        return {"$and": conds}

    def upsert_text_document(
        self,
        *,
        ai: AIClient,
        source: str,
        doc_id: str,
        text: str,
        embedding_model: str,
        chunk_size: int = 1500,
        overlap: int = 200,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Chunk and upsert a document; returns doc_hash used.
        """
        doc_hash = hash_text(text)
        if self._is_indexed(source=source, doc_id=doc_id, doc_hash=doc_hash):
            return doc_hash

        # IMPORTANT: Chroma Cloud validates IDs. Filenames/doc_ids can include spaces and other chars,
        # so do NOT embed doc_id directly into vector IDs.
        # Keep doc_id in metadata for filtering, but use a safe hex prefix for ids.
        safe_prefix = hash_text(f"{source}|{doc_id}|{doc_hash}")
        source_id = f"{source}:{safe_prefix}"
        chunks = chunk_text(text, source_id=source_id, chunk_size=chunk_size, overlap=overlap)
        if not chunks:
            return doc_hash

        embeddings = ai.embed_texts(model=embedding_model, texts=[c.text for c in chunks])
        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas: List[Dict[str, Any]] = []
        for idx, _ in enumerate(chunks):
            md: Dict[str, Any] = {
                "source": source,
                "doc_id": doc_id,
                "doc_hash": doc_hash,
                "chunk_index": idx,
            }
            if extra_metadata:
                md.update(extra_metadata)
            metadatas.append(md)

        # Upsert
        try:
            self._collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
            logger.info("rag.upsert", extra={"source": source, "doc_id": doc_id, "chunks": len(chunks)})
        except Exception as e:
            # Surface useful debugging info for Chroma Cloud validation errors (422).
            logger.warning(
                "rag.upsert_failed",
                extra={
                    "source": source,
                    "doc_id": doc_id,
                    "doc_hash": doc_hash,
                    "chunks": len(chunks),
                    "mode": self.connection_mode(),
                    "collection": self._collection_name,
                    "error": str(e),
                },
            )
            raise
        return doc_hash

    def query(
        self,
        *,
        ai: AIClient,
        source: str,
        query_text: str,
        embedding_model: str,
        top_k: int = 6,
        doc_id: Optional[str] = None,
        doc_hash: Optional[str] = None,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Returns list of (chunk_text, metadata)
        """
        flat: Dict[str, Any] = {"source": source}
        if where_filter:
            flat.update(where_filter)
        if doc_id:
            flat["doc_id"] = doc_id
        if doc_hash:
            flat["doc_hash"] = doc_hash
        where = self._build_where(flat)

        q_emb = ai.embed_texts(model=embedding_model, texts=[query_text])[0]
        res = self._collection.query(
            query_embeddings=[q_emb],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        docs = (res.get("documents") or [[]])[0]
        mds = (res.get("metadatas") or [[]])[0]

        out: List[Tuple[str, Dict[str, Any]]] = []
        for d, md in zip(docs, mds):
            out.append((d, md or {}))
        return out

    def count_chunks(self, *, where_filter: Dict[str, Any], limit: int = 5000) -> Dict[str, Any]:
        """
        Best-effort count of chunks matching a metadata filter.
        Note: some backends may cap results; we return the observed count and the limit used.
        """
        try:
            where = self._build_where(where_filter or {})
            # Chroma Cloud enforces a maximum `get(limit=...)` quota (often 300). Clamp to avoid hard failures.
            effective_limit = int(limit or 0) if limit else 0
            if self.connection_mode() == "cloudclient" and effective_limit > 300:
                effective_limit = 300

            # In Chroma v2, ids are always returned; `include=['ids']` is invalid.
            res = self._collection.get(where=where, limit=effective_limit or 300)
            ids = res.get("ids") or []
            out = {"count": len(ids), "limit": effective_limit or 300, "mode": self.connection_mode(), "collection": self._collection_name}
            if effective_limit != limit:
                out["requested_limit"] = limit
            return out
        except Exception as e:
            return {"count": 0, "limit": limit, "mode": self.connection_mode(), "collection": self._collection_name, "error": str(e)}
