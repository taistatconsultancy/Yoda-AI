# OpenAI in YodaAI — Tasks, Usage, and Prompt Locations

This document explains **what YodaAI uses OpenAI for**, **how to configure/use it**, and **where the prompts live** in this repo.

---

## Tasks powered by OpenAI (what it does)

- **4Ls retrospective chat facilitation**
  - Guides users through **Liked / Learned / Lacked / Longed For**
  - Stores chat messages and responses; generates assistant replies
  - **Backend route**: `app/api/routes/fourls_chat.py`
  - **Also implemented via service**: `app/services/ai_service.py` (older/alternate chat flow)

- **Theme grouping (clustering responses into themes)**
  - Takes retrospective responses and returns theme objects as JSON
  - **Backend route**: `app/api/routes/grouping.py`

- **Discussion facilitation + sprint summary generation**
  - Facilitates a focused discussion on top-voted themes
  - Generates a sprint summary and structured recommendations (JSON)
  - Generates “Disciplined Agile” recommendations using the DA reference doc
  - **Backend route**: `app/api/routes/discussion_summary.py`

- **Onboarding document summarization**
  - Reads uploaded text/PDF/DOCX, stores `source_text`, then generates an AI summary
  - **Backend route**: `app/api/routes/onboarding.py`

---

## Where OpenAI is called (file locations)

### Core OpenAI call sites

- **4Ls chat**
  - `app/api/routes/fourls_chat.py`
  - Uses `OpenAI(...).chat.completions.create(...)`

- **Discussion + summary + DA recommendations**
  - `app/api/routes/discussion_summary.py`
  - Uses `OpenAI(...).chat.completions.create(...)`
  - Uses `response_format={"type":"json_object"}` for the summary endpoint

- **AI theme grouping**
  - `app/api/routes/grouping.py`
  - Uses `OpenAI(...).chat.completions.create(...)` and expects **JSON output**

- **Workspace onboarding summary**
  - `app/api/routes/onboarding.py`
  - Uses `OpenAI(...).chat.completions.create(...)` with `model="gpt-4o-mini"`

### Shared/alternate AI service

- `app/services/ai_service.py`
  - Uses `openai.OpenAI(api_key=...)` and `client.chat.completions.create(...)`
  - Contains additional analysis + action-item generation calls

---

## Prompt locations (where to edit prompts)

In this codebase, **prompts are mostly inline strings in Python files** (no separate prompt template folder).

### 4Ls chat prompts

- **System prompt for the 4Ls chat endpoint**
  - Location: `app/api/routes/fourls_chat.py`
  - Built inline inside `messages_for_ai` (system role content block).

- **System prompt used by the `AIService`**
  - Location: `app/services/ai_service.py`
  - Function: `AIService._get_system_prompt()`

### Theme grouping prompt

- Location: `app/api/routes/grouping.py`
  - Variable: `prompt = f""" ... """` inside the grouping generation handler
  - Also includes a strict “respond with valid JSON only” system message.

### Discussion facilitation + summary prompts

- Location: `app/api/routes/discussion_summary.py`
  - Discussion system prompt: built in `messages_for_ai` as a system role block
  - Summary prompt: `prompt = f"""Analyze this sprint retrospective..."""` (expects JSON)
  - DA recommendations prompt: `prompt = f"""Based on the following themes..."""` (uses DA reference)

### Onboarding summarization prompts

- Location: `app/api/routes/onboarding.py`
  - Builds `prompt = """...""" + source_text`
  - Uses a long system role instruction block defining the required summary structure.

### Prompt/reference documents used as context

- **Disciplined Agile reference**
  - File: `disciplined_agile_scrape.md`
  - Used by:
    - `app/api/routes/discussion_summary.py` (DA recommendations prompt includes the doc)
    - `app/services/enhanced_ai_service.py` (loads it as “discipline_reference” for filtering/response generation)

---

## Configuration (API key + models)

### Environment variable

- **`OPENAI_API_KEY`** is read from environment / `.env`
  - Source: `app/core/config.py` (`settings.OPENAI_API_KEY`)

In your `.env`:

```env
OPENAI_API_KEY=sk-...
```

### Models used (hardcoded in code)

Current hardcoded model strings you’ll see in code:

- `gpt-4` (used in several routes and `AIService`)
- `gpt-4o-mini` (used in onboarding summary)

Note: `app/core/config.py` defines `AI_MODEL`, but most routes currently **hardcode** the model instead of using `settings.AI_MODEL`.

---

## Usage (how to run with OpenAI enabled)

### Backend prerequisites

- Set `OPENAI_API_KEY` in `.env` (or your deployment environment variables)
- Install dependencies from `requirements.txt`
- Start the server (example):
  - `python start_server.py`

### What to test in the app

- **4Ls chat**: start a retrospective chat, send messages, confirm AI replies
- **Grouping**: generate AI grouping for a retrospective with responses
- **Summary**: generate sprint summary and verify JSON parsing works
- **DA recommendations**: generate recommendations (uses `disciplined_agile_scrape.md`)
- **Onboarding summary**: upload a file and run the “generate summary” endpoint

---

## Troubleshooting

- **`OPENAI_API_KEY is not set`**
  - Ensure `.env` exists and is loaded, or set the variable in your deployment host.
  - Confirm `app/core/config.py` loads `.env` (it calls `load_dotenv()`).

- **JSON parsing errors (grouping/summary)**
  - The prompts require “JSON only”. If the model returns markdown fences, the code attempts to strip them in `app/api/routes/grouping.py`.
  - The summary endpoint uses `response_format={"type":"json_object"}` to reduce formatting drift.

---

## Quick reference

- **OpenAI config**: `app/core/config.py`
- **OpenAI calls**: `app/api/routes/{fourls_chat,discussion_summary,grouping,onboarding}.py`, `app/services/ai_service.py`
- **Prompt strings**: inline in the above files
- **Reference doc used in prompts**: `disciplined_agile_scrape.md`

