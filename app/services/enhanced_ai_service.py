"""
Enhanced AI Service using Gemini API for content filtering and PDF reference
"""

import requests
import asyncio
try:
    from huggingface_hub import InferenceClient
except Exception:
    InferenceClient = None
from typing import List, Dict, Any, Optional
import os
from app.core.config import settings
from app.models.retrospective_new import Retrospective
from app.models.user import User
from app.models.workspace import Workspace as Team, WorkspaceMember as TeamMember


class EnhancedAIService:
    """Enhanced AI service using Gemini for content filtering and PDF reference"""
    
    def __init__(self):
        # We'll use Hugging Face as the single external LLM provider for enhanced features.
        # If HF isn't configured, the service will fall back to local/static responses.
        self.model = None
        
        # Load discipline reference
        self.discipline_reference = self._load_discipline_reference()

        # Hugging Face config (set on the instance).
        # Accept HF token from either settings.HUGGINGFACE_API_KEY or the common env var HF_TOKEN
        self.hf_api_key = (
            settings.HUGGINGFACE_API_KEY
            or settings.HF_TOKEN
            or os.getenv('HUGGINGFACE_API_KEY')
            or os.getenv('HF_TOKEN')
        )
        self.hf_model = settings.HUGGINGFACE_MODEL or os.getenv('HUGGINGFACE_MODEL')

        # Normalize values: strip surrounding quotes and whitespace if present
        def _norm(v: Optional[str]) -> Optional[str]:
            if not v:
                return None
            v2 = v.strip()
            if (v2.startswith("'") and v2.endswith("'")) or (v2.startswith('"') and v2.endswith('"')):
                v2 = v2[1:-1].strip()
            return v2 or None

        self.hf_api_key = _norm(self.hf_api_key)
        self.hf_model = _norm(self.hf_model)

        # If a token is present but no model configured, set a safe default so HF is used.
        if self.hf_api_key and not self.hf_model:
            # Default to a small, fast model to avoid large inference times.
            self.hf_model = 'gpt2'
            print(f"Hugging Face token found but no model configured. Defaulting to '{self.hf_model}'. Set HUGGINGFACE_MODEL in .env to change this.")
        elif self.hf_api_key and self.hf_model:
            # Mask the token for logging
            masked = self.hf_api_key[:6] + '...' + self.hf_api_key[-4:]
            print(f"Using Hugging Face model: {self.hf_model} (token {masked})")
        else:
            print("Hugging Face not configured (no token/model); falling back to local responses.")
    
    def _load_discipline_reference(self) -> str:
        """Load the disciplined agile reference file"""
        try:
            discipline_file_path = "disciplined_agile_scrape.md"
            if os.path.exists(discipline_file_path):
                with open(discipline_file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return "Disciplined Agile reference not available"
        except Exception as e:
            print(f"Error loading discipline reference: {e}")
            return "Disciplined Agile reference not available"
    
    async def check_content_appropriateness(
        self, 
        user_message: str, 
        project_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Use Gemini to check if content is appropriate for retrospective context"""
        
        prompt = f"""
        You are a content filter for an agile retrospective AI assistant. Your job is to determine if user input is appropriate for a work-related retrospective discussion.

        CONTEXT:
        - This is a YodaAI retrospective assistant for agile teams
        - Users should discuss work-related topics: sprint performance, team collaboration, technical challenges, process improvements, etc.
        - Reference material available: Disciplined Agile framework
        - Project context: {project_context or "No specific project context provided"}

        DISCIPLINE REFERENCE:
        {self.discipline_reference[:2000]}...

        USER MESSAGE: "{user_message}"

        TASK:
        1. Determine if this message is appropriate for a work retrospective
        2. Check if it relates to agile practices, team work, sprint performance, or process improvement
        3. If inappropriate, provide a polite redirect to retrospective topics
        4. If appropriate, confirm it's work-related

        Respond with JSON format:
        {{
            "is_appropriate": true/false,
            "reason": "brief explanation",
            "redirect_message": "polite redirect if inappropriate, empty if appropriate",
            "confidence": 0.0-1.0
        }}
        """
        
        # If model is not available, skip AI filtering and allow content
        if not self.model:
            return {
                "is_appropriate": True,
                "reason": "No AI model configured, allowing content",
                "redirect_message": "",
                "confidence": 0.5
            }

        try:
            response = self.model.generate_content(prompt)

            # Try to extract text safely from the response object
            text = ''
            if hasattr(response, 'text'):
                text = response.text
            elif hasattr(response, 'content'):
                # some SDKs may use .content
                text = response.content
            else:
                text = str(response)

            # Parse JSON response if possible
            import json
            try:
                result = json.loads(text)
                return result
            except Exception as je:
                # Log the raw response for debugging and fall back
                print(f"Error parsing JSON from content filter response: {je}. Raw response (truncated): {text[:500]}")
                return {
                    "is_appropriate": True,
                    "reason": "Content filter returned non-JSON, allowing content",
                    "redirect_message": "",
                    "confidence": 0.5
                }
        except Exception as e:
            print(f"Error in content filtering: {e}")
            # Fallback to basic check
            return {
                "is_appropriate": True,
                "reason": "Error in AI filtering, allowing content",
                "redirect_message": "",
                "confidence": 0.5
            }
    
    async def generate_retrospective_response(
        self,
        user_message: str,
        current_step: str,
        chat_history: List[Dict] = None,
        project_context: Optional[str] = None,
        uploaded_documents: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate AI response using Gemini with project context and discipline reference"""
        
        if chat_history is None:
            chat_history = []
        
        # First check content appropriateness
        content_check = await self.check_content_appropriateness(user_message, project_context)
        
        if not content_check["is_appropriate"]:
            return {
                "response": content_check["redirect_message"],
                "follow_up_questions": [],
                "confidence": content_check["confidence"],
                "metadata": {
                    "model": "gemini-content-filtered",
                    "step": current_step,
                    "filtered": True,
                    "reason": content_check["reason"]
                }
            }
        
        # Generate contextual response
        prompt = f"""
        You are YodaAI, a conversational AI assistant specialized in facilitating 4Ls retrospectives for agile teams using Disciplined Agile principles.

        PROJECT CONTEXT:
        {project_context or "No specific project context provided"}

        UPLOADED DOCUMENTS:
        {uploaded_documents or "No documents uploaded"}

        DISCIPLINE REFERENCE (Disciplined Agile):
        {self.discipline_reference[:3000]}...

        CURRENT RETROSPECTIVE STEP: {current_step}
        USER MESSAGE: "{user_message}"

        CHAT HISTORY:
        {self._format_chat_history(chat_history)}

        INSTRUCTIONS:
        1. Respond naturally and conversationally
        2. Reference the project context and uploaded documents when relevant
        3. Apply Disciplined Agile principles and practices
        4. Ask thoughtful follow-up questions to deepen insights
        5. Help identify patterns and suggest actionable improvements
        6. Keep responses under 150 words
        7. Be encouraging and supportive
        8. Focus on work-related retrospective topics only

        RESPONSE FORMAT:
        Provide a natural, conversational response that:
        - Acknowledges what the user shared
        - References project context or documents if relevant
        - Applies DA principles when appropriate
        - Asks one focused follow-up question
        - Maintains a warm, professional tone
        """
        
        # If Hugging Face is configured, prefer it (free community models)
        if self.hf_api_key and self.hf_model:
            try:
                # call HF in a thread to avoid blocking the event loop
                hf_resp = await asyncio.to_thread(self._call_huggingface, prompt)
                # Optionally post-correct grammar using a dedicated HF model or the same model
                final_text = hf_resp
                try:
                    enable_pc = getattr(settings, 'HUGGINGFACE_ENABLE_POSTCORRECT', False)
                except Exception:
                    enable_pc = False

                if enable_pc:
                    try:
                        # model to use for correction can be configured, otherwise reuse hf_model
                        pc_model = getattr(settings, 'HUGGINGFACE_GRAMMAR_MODEL', None) or self.hf_model
                        corrected = await asyncio.to_thread(self._call_huggingface_correction, final_text, pc_model)
                        if corrected:
                            final_text = corrected
                    except Exception as e:
                        print(f"Grammar correction failed: {e}")

                # Always apply a light local cleanup as a safety net
                final_text = self.clean_text_basic(final_text)

                return {
                    "response": final_text,
                    "follow_up_questions": self._generate_follow_up_questions(current_step, user_message),
                    "confidence": 0.85,
                    "metadata": {
                        "model": self.hf_model,
                        "provider": "huggingface",
                        "step": current_step,
                    }
                }
            except Exception as e:
                print(f"Error generating response from Hugging Face: {e}")

        # If Gemini configured, use it; otherwise fallback
        if self.model:
            try:
                response = self.model.generate_content(prompt)

                return {
                    "response": response.text,
                    "follow_up_questions": self._generate_follow_up_questions(current_step, user_message),
                    "confidence": 0.9,
                    "metadata": {
                        "model": getattr(self.model, 'name', 'gemini'),
                        "step": current_step,
                        "project_context_used": bool(project_context),
                        "documents_referenced": bool(uploaded_documents)
                    }
                }
            except Exception as e:
                print(f"Error generating response: {e}")

        return self._get_fallback_response(current_step)

    def _call_huggingface(self, prompt: str) -> str:
        """Call Hugging Face Inference API (text generation) and return text output.

        Note: Uses the POST /models/{model} endpoint. For short / community models this
        should work with an API token. If you're using the free Inference API for a
        publicly-hosted model, set HUGGINGFACE_MODEL to the model id (e.g. 'gpt2' or
        'huggingface/llama-...' depending on availability).
        """
        if not self.hf_api_key or not self.hf_model:
            raise RuntimeError('Hugging Face model or API key not configured')

        # Prefer using the huggingface_hub.InferenceClient.chat_completion if available
        if InferenceClient is not None:
            try:
                client = InferenceClient(token=self.hf_api_key, model=self.hf_model)
                # Use chat_completion to provide chat-style messages
                response = client.chat_completion(
                    model=self.hf_model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Use the following context to answer the question."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7,
                )

                # Response shape: response.choices[0].message["content"] per user example
                try:
                    return response.choices[0].message.get("content")
                except Exception:
                    # Fallback to string conversion
                    return str(response)
            except Exception as e:
                # If InferenceClient call fails, fall through to REST fallback
                print(f"InferenceClient.chat_completion failed: {e}")

        # REST fallback to HF Inference API
        url = f'https://api-inference.huggingface.co/models/{self.hf_model}'
        headers = {
            'Authorization': f'Bearer {self.hf_api_key}',
            'Accept': 'application/json'
        }
        payload = {
            'inputs': prompt,
            'parameters': { 'max_new_tokens': 150, 'temperature': 0.7 }
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # The HF inference API returns different shapes; try to extract text safely
        if isinstance(data, dict) and 'error' in data:
            raise RuntimeError(f"Hugging Face API error: {data.get('error')}")

        # If the model returns a list of generated texts
        if isinstance(data, list):
            first = data[0]
            if isinstance(first, dict) and 'generated_text' in first:
                return first['generated_text']
            if isinstance(first, str):
                return first

        # If single dict with 'generated_text'
        if isinstance(data, dict) and 'generated_text' in data:
            return data['generated_text']

        # Fallback: string representation
        return str(data)

    def clean_text_basic(self, text: str) -> str:
        """Basic cleanup: fix spacing, punctuation and capitalization."""
        import re
        if not text:
            return text

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Fix spaces before punctuation: "word ." -> "word."
        text = re.sub(r'\s+([?.!,;:])', r'\1', text)

        # Ensure a space after punctuation if missing: "word.This" -> "word. This"
        text = re.sub(r'([?.!,;:])([A-Za-z0-9\"])', r'\1 \2', text)

        # Remove duplicate punctuation like "??" or ".." to a single char
        text = re.sub(r'([?.!,;:])\1+', r'\1', text)

        # Capitalize sentence starts
        def cap_sentence(m):
            return m.group(1) + m.group(2).upper()
        text = re.sub(r'(^|[\.\?\!]\s+)([a-z])', cap_sentence, text)

        return text

    def _call_huggingface_correction(self, text: str, model: str) -> str:
        """Use HF to correct grammar: sends a brief instruction with the text and returns corrected text."""
        if not self.hf_api_key or not model:
            raise RuntimeError('Hugging Face correction model or API key not configured')

        instruction = (
            "You are a copy editor. Correct the grammar, punctuation, spacing and capitalization of the following text, "
            "preserving meaning and tone. Return only the corrected text.\n\n" + text
        )

        # Try InferenceClient if available
        if InferenceClient is not None:
            try:
                client = InferenceClient(token=self.hf_api_key, model=model)
                resp = client.text_generation(
                    inputs=instruction,
                    max_new_tokens=getattr(settings, 'HUGGINGFACE_MAX_TOKENS', 150),
                    temperature=getattr(settings, 'HUGGINGFACE_TEMPERATURE', 0.3)
                )
                # Extract
                if isinstance(resp, list) and resp:
                    first = resp[0]
                    if isinstance(first, dict) and 'generated_text' in first:
                        return first['generated_text']
                    if isinstance(first, str):
                        return first
                if isinstance(resp, dict) and 'generated_text' in resp:
                    return resp['generated_text']
                return str(resp)
            except Exception as e:
                print(f"InferenceClient correction call failed: {e}")

        # REST fallback
        url = f'https://api-inference.huggingface.co/models/{model}'
        headers = {'Authorization': f'Bearer {self.hf_api_key}'}
        payload = {'inputs': instruction, 'parameters': {'max_new_tokens': getattr(settings, 'HUGGINGFACE_MAX_TOKENS', 150), 'temperature': getattr(settings, 'HUGGINGFACE_TEMPERATURE', 0.3)}}
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            first = data[0]
            if isinstance(first, dict) and 'generated_text' in first:
                return first['generated_text']
            if isinstance(first, str):
                return first
        if isinstance(data, dict) and 'generated_text' in data:
            return data['generated_text']
        return str(data)
    
    def _format_chat_history(self, chat_history: List[Dict]) -> str:
        """Format chat history for the prompt"""
        if not chat_history:
            return "No previous conversation"
        
        formatted = []
        for msg in chat_history[-5:]:  # Last 5 messages
            role = "User" if msg.get("role") == "user" else "YodaAI"
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)
    
    def _generate_follow_up_questions(self, current_step: str, user_message: str) -> List[str]:
        """Generate contextual follow-up questions based on current step"""
        step_questions = {
            "liked": [
                "What made this particularly effective?",
                "How can we replicate this success?",
                "What factors contributed to this positive outcome?"
            ],
            "learned": [
                "How will this knowledge help the team?",
                "What was the most surprising part of this learning?",
                "How can we apply this insight going forward?"
            ],
            "lacked": [
                "What could we do differently next time?",
                "What was the root cause of this challenge?",
                "How can we prevent this from happening again?"
            ],
            "longed_for": [
                "What would need to change to make this possible?",
                "Who would need to be involved in implementing this?",
                "What would be the first step towards this goal?"
            ]
        }
        
        return step_questions.get(current_step, ["Tell me more about that."])
    
    def _get_fallback_response(self, current_step: str) -> Dict[str, Any]:
        """Fallback response if AI fails"""
        fallback_responses = {
            "liked": "That's great to hear! What else went particularly well this sprint?",
            "learned": "That's a valuable learning! How do you think this knowledge will help the team?",
            "lacked": "I understand this was challenging. What do you think could have been done differently?",
            "longed_for": "That's a great vision for improvement! What would need to change to make this possible?"
        }
        
        return {
            "response": fallback_responses.get(current_step, "Thanks for sharing that! Could you tell me more?"),
            "follow_up_questions": [],
            "confidence": 0.7,
            "metadata": {
                "model": "fallback",
                "step": current_step,
                "error": True
            }
        }
    
    async def analyze_retrospective_patterns(
        self, 
        responses: List[Dict],
        project_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze retrospective patterns using Gemini"""
        
        prompt = f"""
        Analyze the following retrospective responses and provide insights using Disciplined Agile principles.

        PROJECT CONTEXT:
        {project_context or "No specific project context provided"}

        DISCIPLINE REFERENCE:
        {self.discipline_reference[:2000]}...

        RETROSPECTIVE RESPONSES:
        {self._format_responses_for_analysis(responses)}

        Provide analysis in JSON format:
        {{
            "key_themes": ["theme1", "theme2", "theme3"],
            "action_items": [
                {{"action": "description", "priority": "high/medium/low", "owner": "suggested_owner"}}
            ],
            "insights": ["insight1", "insight2"],
            "recommendations": ["recommendation1", "recommendation2"],
            "da_principles_applied": ["principle1", "principle2"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"Error in pattern analysis: {e}")
            return {
                "key_themes": ["Team collaboration", "Process improvement"],
                "action_items": [],
                "insights": ["Team is focused on continuous improvement"],
                "recommendations": ["Continue current practices"],
                "da_principles_applied": ["Relentless Improvement"]
            }
    
    def _format_responses_for_analysis(self, responses: List[Dict]) -> str:
        """Format responses for analysis"""
        formatted = []
        for i, response in enumerate(responses, 1):
            step = response.get("step", "unknown")
            content = response.get("content", "")
            formatted.append(f"{i}. {step.upper()}: {content}")
        
        return "\n".join(formatted)
