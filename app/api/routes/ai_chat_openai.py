"""
OpenAI-backed AI chat routes (thematic analysis + session creation)
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
import uuid
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.retrospective_new import ChatSession, ChatMessage
from app.schemas.ai_chat import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageResponse,
)
from app.services.ai_chat_service import AIChatService
from app.services.firebase_service import FirebaseService
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.api.dependencies.auth import get_current_user
from app.core.config import settings
import os

router = APIRouter()


class ThematicRequest(BaseModel):
    text: str
    session_type: Optional[str] = "retrospective"
    current_step: Optional[str] = "liked"


def call_openai_thematic_analysis(text: str) -> Dict[str, Any]:
    """Perform a simple thematic analysis using OpenAI's API.

    This function expects `OPENAI_API_KEY` to be available in settings or env.
    It returns a dict with 'summary' and 'themes' keys.
    """
    # Prefer the new OpenAI client (openai>=1.0.0)
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not configured in settings or environment")

    # Prompt guidance:
    # - Limit the total number of grouped themes to a reasonable number to keep results concise.
    # - Create a special group named 'Missing Group' that collects examples which are meaningfully different
    #   from other themes (unique opinions, one-off issues, or contradictory points).
    # - For themes, include a short 'theme' string and 'examples' (2-5 representative excerpts).
    # - Return strictly parseable JSON. If unsure, return an object with 'summary' and 'themes' keys where
    #   'themes' is an array. Prefer no extra keys.
    max_themes = 8
    prompt = (
        f"Perform a thematic analysis of the following text. Return a JSON object with keys: 'summary' (a concise paragraph),"
        f" and 'themes' (a list of objects with 'theme' and 'examples' where examples are representative excerpts).\n\n"
        f"Constraints:\n- Limit the total number of grouped themes (including the special 'Missing Group' group) to at most {max_themes}.\n"
        "- Create a special group named 'Missing Group' to collect examples that are meaningfully different from the main clusters"
        " (e.g., unique opinions, one-off issues, or contradictory points).\n"
        "- For each theme, include a 'theme' (short title) and 'examples' (array with 2-5 short excerpts).\n"
        "- Order themes by relevance/size (largest themes first); put the 'Missing Group' group last.\n"
        "- Return strictly valid JSON and avoid commentary outside the JSON. If you cannot form themes, return an empty 'themes' list.\n\n"
        "Context:\n" + text
    )

    content = ""
    # Try modern openai client first
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=getattr(settings, "OPENAI_MODEL", "gpt-4"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.2,
        )

        # Attempt to read response content from possible structures
        try:
            # object-style
            content = resp.choices[0].message.content
        except Exception:
            try:
                # dict-like
                content = resp["choices"][0]["message"]["content"]
            except Exception:
                content = str(resp)

    except Exception:
        # Fallback for older openai package versions
        try:
            import openai
            openai.api_key = api_key
            resp = openai.ChatCompletion.create(
                model=getattr(settings, "OPENAI_MODEL", "gpt-4"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.2,
            )
            try:
                content = resp["choices"][0]["message"]["content"]
            except Exception:
                content = str(resp)
        except Exception as e:
            raise RuntimeError(f"openai client error: {e}")


    # Try to extract JSON from the model output
    import json

    try:
        data = json.loads(content)
    except Exception:
        # If output is not strict JSON, wrap it as summary text
        data = {"summary": content, "themes": []}

    return data


def retrieve_with_chroma(text: str, top_k: int = 3):
    """Use Chroma to retrieve top_k related documents for the given text.
    Returns list of docs (strings). If Chroma not configured or errors, returns [].
    """
    try:
        import importlib
        chromadb = importlib.import_module("chromadb")
        OpenAI = importlib.import_module("openai").OpenAI
    except Exception:
        return []

    CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
    CHROMA_TENANT = os.getenv("CHROMA_TENANT") or os.getenv("chroma_Tenant")
    collection_name = os.getenv("CHROMA_COLLECTION", "thematic_embeddings")

    try:
        # connect to Chromadb cloud if API key present, otherwise try local client
        if CHROMA_API_KEY:
            client = chromadb.CloudClient(api_key=CHROMA_API_KEY, tenant=CHROMA_TENANT)
        else:
            client = chromadb.Client()

        collection = client.get_collection(collection_name)
    except Exception:
        return []

    # create embedding for the query text using OpenAI embeddings
    try:
        client_embed = OpenAI(api_key=settings.OPENAI_API_KEY)
        emb_resp = client_embed.embeddings.create(model="text-embedding-ada-002", input=text)
        vector = emb_resp.data[0].embedding
    except Exception:
        return []

    try:
        results = collection.query(query_embeddings=[vector], n_results=top_k)
        docs = results.get("documents", [[]])[0]
        print('Chroma retrieved docs')
        return docs
    except Exception:
        return []


@router.post("/thematic-analysis")
async def thematic_analysis(
    file: UploadFile = File(...),
    session_type: Optional[str] = Form("retrospective"),
    current_step: Optional[str] = Form("liked"),
    # db: Session = Depends(get_db),
):
    """Run thematic analysis on an uploaded file's text. Previously this endpoint created
    and persisted a DB-backed session; that code is commented below for reference.
    """
    # Read uploaded file contents
    try:
        raw = await file.read()
        try:
            text = raw.decode("utf-8")
        except Exception:
            text = str(raw)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {e}")

    # --- Previously used DB/session creation (kept commented for reference) ---
    # service = AIChatService(db)
    # session_create = ChatSessionCreate(
    #     retrospective_id=None,
    #     session_type=session_type,
    #     current_step=current_step,
    #     context={"source": "thematic_analysis"},
    # )
    # chat_session = service.create_chat_session(session_create, 0)
    # -------------------------------------------------------------------------

    # Optionally run retrieval-augmented generation: get related docs from Chroma
    try:
        retrieved = retrieve_with_chroma(text, top_k=3)
    except Exception:
        retrieved = []

    # Build context: uploaded text + retrieved docs (if any)
    if retrieved:
        context = text + "\n\nRetrieved documents:\n" + "\n\n".join(retrieved)
    else:
        context = text

    # Call OpenAI to perform thematic analysis on the combined context
    try:
        analysis = call_openai_thematic_analysis(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

    # Represent AI message as a plain dict (avoid instantiating ORM-mapped ChatMessage
    # when DB/ORM configuration may not be fully initialized). If you re-enable
    # persistence below you can construct a ChatMessage instance at that time.
    ai_message = {
        "session_id": 0,
        "content": analysis.get("summary") or "",
        "message_type": "ai",
        "ai_model": getattr(settings, "OPENAI_MODEL", "gpt-4"),
        "ai_confidence": 100,
        "ai_metadata": {"analysis_themes": analysis.get("themes", [])},
    }

    # NOTE: persistence to Firestore/SQL was previously done here. It's commented out
    # to make the endpoint operate on uploaded files without requiring DB connectivity.
    # If you want to re-enable persistence, uncomment and adapt the code below.

    # firebase = getattr(service, "firebase", None)
    # if firebase and firebase.enabled:
    #     firebase.save_message(chat_session.session_id, {
    #         "content": ai_message.content,
    #         "message_type": ai_message.message_type,
    #         "ai_model": ai_message.ai_model,
    #         "ai_confidence": ai_message.ai_confidence,
    #         "ai_metadata": ai_message.ai_metadata,
    #         "created_at": __import__("datetime").datetime.utcnow().isoformat()
    #     })
    # else:
    #     try:
    #         if hasattr(chat_session, "id") and chat_session.id:
    #             sql_msg = ChatMessage(
    #                 session_id=chat_session.id,
    #                 content=ai_message.content,
    #                 message_type=ai_message.message_type,
    #                 ai_model=ai_message.ai_model,
    #                 ai_confidence=ai_message.ai_confidence,
    #                 ai_metadata=ai_message.ai_metadata,
    #             )
    #             db.add(sql_msg)
    #             db.commit()
    #             db.refresh(sql_msg)
    #             ai_message = sql_msg
    #     except Exception as e:
    #         print(f"Warning: failed to persist AI message to SQL DB: {e}")

    # Return a lightweight session id for the uploaded analysis (no DB session created)
    return {
        "session": {
            "session_id": str(uuid.uuid4()),
            "session_type": session_type,
            "filename": getattr(file, 'filename', None)
        },
        "analysis": analysis,
    }
