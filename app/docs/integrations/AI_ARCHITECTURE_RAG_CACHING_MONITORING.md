# AI Architecture Upgrade (OpenAI + Chroma RAG + Caching + Monitoring)

This document describes the AI feature upgrades implemented in this repo:

1. **Prompts extracted into dedicated files**
2. **Centralized AI architecture (`app/ai/`)**
3. **RAG with ChromaDB (embeddings) for large documents**
4. **Response caching (hash-based)**
5. **Token monitoring + guardrails**

---

## 1) Extract prompts into dedicated files

### What changed

All major prompts used by OpenAI are now stored under:

- `app/ai/prompts/`

### Why

- Easier prompt iteration
- Avoids duplicated prompt strings across routes
- Enables cache keys to incorporate a stable “prompt template” string

### Prompt files added

- **4Ls chat**
  - `app/ai/prompts/fourls_system.md`
- **Theme grouping**
  - `app/ai/prompts/grouping_prompt.md`
- **Sprint summary**
  - `app/ai/prompts/sprint_summary_prompt.md`
- **DA recommendations**
  - `app/ai/prompts/da_recommendations_prompt.md`
- **Discussion facilitation**
  - `app/ai/prompts/discussion_facilitator_system.md`
  - `app/ai/prompts/discussion_general_system.md`
- **Onboarding summary**
  - `app/ai/prompts/onboarding_summary_system.md`
  - `app/ai/prompts/onboarding_summary_user.md`

---

## 2) Centralized AI architecture (no OpenAI calls in routes)

### What changed

OpenAI usage is centralized in:

- `app/ai/openai_client.py` (the only OpenAI client wrapper)

Routes now act as “thin controllers” and call feature modules:

- `app/ai/features/*`

### Why

This removes duplicated model choices, duplicated OpenAI client creation, and scattered prompt strings.

### Key files

- **Prompt loading**
  - `app/ai/prompt_loader.py`
- **OpenAI wrapper + monitoring**
  - `app/ai/openai_client.py`
- **Feature modules**
  - `app/ai/features/grouping.py`
  - `app/ai/features/sprint_summary.py`
  - `app/ai/features/da_recommendations.py`
  - `app/ai/features/onboarding_summary.py`
  - `app/ai/features/discussion.py`
  - `app/ai/features/fourls_chat.py`

---

## 3) Handle large documents via embeddings (RAG with ChromaDB)

### Current issue (before)

- Large documents (e.g. `disciplined_agile_scrape.md`, onboarding uploaded documents) were injected directly into prompts.
- This increases token usage and latency, and may exceed context windows.

### What changed

We use **RAG**:

- Chunk the document once
- Generate embeddings once
- Store chunks + vectors in **ChromaDB**
- For each request, retrieve only the **top-k relevant chunks**

### Chroma implementation

- **Chunking**
  - `app/ai/rag/chunking.py` (simple character chunking with overlap)
- **Vector store**
  - `app/ai/rag/chroma_store.py`

### RAG data model (what we store in Chroma)

Each chunk is upserted with:

- **id**: safe, deterministic, hex-based chunk IDs (filenames may contain spaces/special chars; we do **not** embed raw filenames into IDs)
- **document text**: the chunk’s text content
- **embedding**: generated via `AIClient.embed_texts(...)`
- **metadata** (used for filtering):
  - `source`: `"onboarding"` (for onboarding/project docs)
  - `workspace_id`: integer workspace id (workspace-scoped retrieval)
  - `doc_id`: string (workspace_id + filename + hash)
  - `doc_hash`: string (sha256 of extracted text)
  - `chunk_index`: integer
  - plus extras like `filename`, `uploaded_at`

### Important: Chroma Cloud filter syntax + quotas

Chroma Cloud (v2) enforces:

- **Operator-based `where` filters** (not plain dicts):
  - single condition: `{"workspace_id": {"$eq": 14}}`
  - multiple: `{"$and": [{"source": {"$eq": "onboarding"}}, {"workspace_id": {"$eq": 14}}]}`
  - Implemented via `ChromaStore._build_where(...)`
- **`get(limit=...)` quota**:
  - Cloud commonly caps `get(limit)` around **300**
  - `ChromaStore.count_chunks(...)` clamps higher limits to avoid “quota exceeded” errors

### Documents using RAG

- **Disciplined Agile recommendations**
  - Source file: `disciplined_agile_scrape.md`
  - Retrieval query: themes text derived from retro topics
  - Feature: `app/ai/features/da_recommendations.py`

- **Onboarding summaries**
  - **New workflow**: upload documents via the **Project Documents** tab
    - API: `POST /api/v1/workspaces/{workspace_id}/documents/upload`
    - Route: `app/api/routes/workspace_documents.py`
    - Each upload extracts text, stores metadata in `UserOnboarding.onboarding_data["documents"]`, and indexes to Chroma in a background task.
  - Summary generation:
    - API: `POST /api/v1/workspaces/{workspace_id}/onboarding/generate`
    - Route: `app/api/routes/onboarding.py`
    - Generates even if `source_text` is absent, by using RAG over all `workspace_id` documents.
  - Feature: `app/ai/features/onboarding_summary.py`
  - Status/debug:
    - API: `GET /api/v1/workspaces/{workspace_id}/onboarding/rag-status`
    - Returns chunk count + a small retrieval probe (workspace-scoped).

### Config knobs

In `app/core/config.py`:

- `AI_EMBEDDING_MODEL` (default `text-embedding-3-small`)
- `AI_RAG_TOP_K` (default `8`)
- `CHROMA_PERSIST_DIR` (default `./.chroma`)
- `CHROMA_COLLECTION` (default `thematic_embeddings`)

---

## 4) Response caching (hash-based)

### Current issue (before)

Identical AI requests (same prompt + same inputs + same model) were recomputed repeatedly.

### What changed

We introduced a DB-backed cache keyed by a deterministic hash of:

- Prompt template (string)
- Inputs (JSON)
- Model name

### Cache implementation

- Cache table is created at runtime if missing (no Alembic required):
  - `app/ai/cache.py`
  - Table: `ai_response_cache`

### Cache key

- `sha256( stable_json(prompt + inputs + model) )`
  - Implemented in: `app/ai/utils.py` (`hash_cache_key`)

### Features that use caching

- **Theme grouping** (`app/ai/features/grouping.py`)
- **Sprint summaries** (`app/ai/features/sprint_summary.py`)
- **DA recommendations** (`app/ai/features/da_recommendations.py`)
- **Onboarding summaries** (`app/ai/features/onboarding_summary.py`)

---

## 5) Token monitoring + guardrails

### Current issue (before)

No visibility into token usage per feature; prompt regressions could silently increase cost/latency.

### What changed

All AI requests are executed via:

- `app/ai/openai_client.py` (`AIClient.chat_complete`)

This logs (per request):

- endpoint name (feature identifier)
- model used
- prompt tokens
- completion tokens
- total tokens

Guardrails:

- Warn if total tokens exceed `AI_TOKEN_SPIKE_THRESHOLD`
- Warn if completion tokens exceed `AI_MAX_OUTPUT_TOKENS`

Config:

- `AI_TOKEN_SPIKE_THRESHOLD` (default `8000`)
- `AI_MAX_OUTPUT_TOKENS` (default `2000`)

Note: “alerts” are implemented as **warnings in logs**. For production alerting, wire these log events into your logging/monitoring stack (e.g., Vercel logs + alerts, Datadog, Sentry).

---

## Operational notes

### Dependencies

ChromaDB is now enabled in `requirements.txt`:

- `chromadb==1.1.1`

### Where vectors are stored

Default (development only): local persistent storage:

- `./.chroma/`

For **Vercel / serverless** and production, use **Chroma Cloud** (recommended) or a remote Chroma deployment.

### Chroma Cloud environment variables (recommended)

Set these in your deployment environment (e.g., Vercel Environment Variables):

- `CHROMA_FORCE_CLOUD=true` (recommended to avoid local fallback)
- `CHROMA_API_KEY`
- `CHROMA_TENANT`
- `CHROMA_DATABASE` (optional; **set this if your Chroma Cloud database name is not the default**, e.g. `Novel`)
- `CHROMA_COLLECTION` (optional)

If your installed `chromadb` exposes `chromadb.CloudClient`, the app will use it automatically when the three variables above are set.

If `CloudClient` is not available, the app falls back to `HttpClient`, in which case you must also set:

- `CHROMA_HOST`
- `CHROMA_PORT` (usually `443`)
- `CHROMA_SSL=true`
- `CHROMA_HEADERS_JSON` (optional) to provide the exact auth header required by your Chroma Cloud deployment, e.g. `{"X-Chroma-Token":"..."}`

### Troubleshooting (Chroma Cloud)

- **“Database default does not match Novel…”**
  - Set `CHROMA_DATABASE=Novel` (or your actual database name) in your environment.
- **“Expected where to have exactly one operator …”**
  - Your SDK is enforcing v2 `where` syntax; this repo uses `ChromaStore._build_where()` to generate operator filters.
- **“Quota exceeded … get(limit) … exceeds limit of 300”**
  - Cloud enforces a `get(limit)` cap; the repo clamps counts to stay within quota. Prefer using `query(n_results=top_k)` for retrieval.

### Remote/self-hosted Chroma (HTTP)

To use a remote Chroma server (not CloudClient), set:

- `CHROMA_HOST`
- `CHROMA_PORT`
 - `CHROMA_SSL` (optional, default true)
 - `CHROMA_HEADERS_JSON` (optional)

---

## Quick map: routes → AI features

- `app/api/routes/grouping.py` → `app/ai/features/grouping.py`
- `app/api/routes/discussion_summary.py`
  - discussion facilitation → `app/ai/features/discussion.py`
  - sprint summary → `app/ai/features/sprint_summary.py`
  - DA recommendations → `app/ai/features/da_recommendations.py` (RAG)
- `app/api/routes/onboarding.py` → `app/ai/features/onboarding_summary.py` (RAG + caching)
- `app/api/routes/fourls_chat.py` → `app/ai/features/fourls_chat.py`

