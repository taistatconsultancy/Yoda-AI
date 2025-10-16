"""
Enhanced AI Service using Gemini API for content filtering and PDF reference
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
import os
from app.core.config import settings
from app.models.retrospective import Retrospective
from app.models.user import User
from app.models.team import Team, TeamMember


class EnhancedAIService:
    """Enhanced AI service using Gemini for content filtering and PDF reference"""
    
    def __init__(self):
        # Prefer GEMINI_API_KEY from settings, but also accept GOOGLE_API_KEY or GEMINI_API_KEY in env
        gemini_key = settings.GEMINI_API_KEY or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.model = None

        if not gemini_key:
            # Don't raise here; allow the application to run and fallback to local generators
            print("Warning: No Gemini API key found (GEMINI_API_KEY or GOOGLE_API_KEY). Enhanced AI features will be disabled until a key is provided.")
        else:
            try:
                genai.configure(api_key=gemini_key)
                # Try a few likely model ids; SDKs/regions may expose different names
                tried_models = ['gemini-2.5-pro', 'gemini-pro', 'gemini-1.0', 'text-bison-001']
                for m in tried_models:
                    try:
                        self.model = genai.GenerativeModel(m)
                        break
                    except Exception:
                        self.model = None

                if not self.model:
                    print("Warning: No Gemini model could be initialized. Enhanced AI features will be limited.")
            except Exception as e:
                print(f"Warning: Failed to configure Gemini client: {e}")
        
        # Load discipline reference
        self.discipline_reference = self._load_discipline_reference()
    
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
        
        # If model isn't configured, return a fallback response immediately
        if not self.model:
            return self._get_fallback_response(current_step)

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
