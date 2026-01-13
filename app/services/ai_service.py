"""
AI service for handling chat interactions and retrospective assistance
"""

import openai
from typing import Dict, List, Optional, Any
from app.core.config import settings
import json
import uuid


class AIService:
    """AI service for retrospective assistance"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for YodaAI"""
        return """
        You are YodaAI, a conversational AI assistant specialized in facilitating 4Ls retrospectives for agile teams. 
        You're working on a project called "YodaAI" - an AI-powered retrospective assistant for agile teams.
        
        Your role is to guide teams through structured retrospectives using the 4Ls framework:
        1. **Liked** - What did you like about this sprint?
        2. **Learned** - What did you learn?
        3. **Lacked** - What didn't go well or was lacking?
        4. **Longed For** - What do you wish had happened differently?
        
        Your personality and approach:
        - Be conversational, friendly, and natural - like talking to a helpful colleague
        - Respond appropriately to casual greetings (hi, hello, how are you) with warmth
        - Ask thoughtful follow-up questions to deepen insights
        - Help identify patterns and themes
        - Suggest actionable improvements
        - Keep the conversation flowing naturally
        - Be encouraging about both successes and challenges
        - Use emojis sparingly but effectively
        - Reference agile best practices when relevant
        
        Conversation Guidelines:
        - Respond naturally to greetings: "Hi there! Great to see you. Ready to dive into your retrospective?"
        - For casual responses like "hello" or "how are you", acknowledge warmly and guide to retrospective
        - Always acknowledge what the user has shared before asking follow-ups
        - Ask one focused follow-up question at a time
        - Help users think deeper about their experiences
        - Suggest connections between different 4Ls categories
        - When appropriate, suggest specific action items
        - Keep responses conversational and under 100 words
        
        IMPORTANT CONTENT FILTERING:
        - If user input contains inappropriate content (drugs, violence, political topics, etc.), politely redirect to retrospective topics
        - If user input is off-topic, gently guide them back to the 4Ls framework
        - Always maintain a professional, supportive tone
        - Focus exclusively on work-related retrospective topics
        
        Remember: You're facilitating reflection through natural conversation. Be warm, conversational, and supportive while staying focused on agile retrospectives.
        """
    
    async def generate_response(
        self, 
        user_message: str, 
        current_step: str = "liked",
        chat_history: List[Dict] = None,
        context: Dict = None
    ) -> Dict[str, Any]:
        """Generate AI response for retrospective chat"""
        
        if chat_history is None:
            chat_history = []
        
        # Content filtering - check for inappropriate content
        if self._is_inappropriate_content(user_message):
            return {
                "response": self._get_redirect_response(current_step),
                "follow_up_questions": [],
                "confidence": 0.8,
                "metadata": {
                    "model": "content-filtered",
                    "step": current_step,
                    "filtered": True
                }
            }
        
        # Build conversation context
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add chat history
        for msg in chat_history[-10:]:  # Keep last 10 messages for context
            messages.append({
                "role": "user" if msg["type"] == "user" else "assistant",
                "content": msg["content"]
            })
        
        # Add current user message with step context
        step_context = f"[Current 4Ls step: {current_step.upper()}] "
        messages.append({
            "role": "user", 
            "content": step_context + user_message
        })
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=200,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Generate follow-up questions
            follow_up_questions = await self._generate_follow_up_questions(
                user_message, ai_response, current_step
            )
            
            return {
                "response": ai_response,
                "follow_up_questions": follow_up_questions,
                "confidence": 0.9,  # High confidence for GPT-4
                "metadata": {
                    "model": "gpt-4",
                    "step": current_step,
                    "tokens_used": response.usage.total_tokens if response.usage else 0
                }
            }
            
        except Exception as e:
            # Fallback response if AI fails
            return {
                "response": self._get_fallback_response(current_step),
                "follow_up_questions": [],
                "confidence": 0.5,
                "metadata": {"error": str(e)}
            }
    
    async def _generate_follow_up_questions(
        self, 
        user_message: str, 
        ai_response: str, 
        current_step: str
    ) -> List[str]:
        """Generate follow-up questions based on context"""
        
        follow_up_prompts = {
            "liked": [
                "What specifically made this work well?",
                "How can we ensure this continues?",
                "What factors contributed to this success?"
            ],
            "learned": [
                "How will this learning help the team?",
                "What would you do differently next time?",
                "How can we share this knowledge?"
            ],
            "lacked": [
                "What could have been done differently?",
                "How did this impact the team?",
                "What steps could prevent this?"
            ],
            "longed_for": [
                "What would need to change to make this happen?",
                "How could we work towards this?",
                "What's the first step?"
            ]
        }
        
        # Return 1-2 relevant follow-up questions
        questions = follow_up_prompts.get(current_step, [])
        return questions[:2] if questions else []
    
    def _get_fallback_response(self, current_step: str) -> str:
        """Get fallback response if AI fails"""
        fallback_responses = {
            "liked": "That's great to hear! What else went particularly well this sprint? I'd love to learn more about what made it successful.",
            "learned": "That's a valuable learning! How do you think this knowledge will help the team in future sprints?",
            "lacked": "I understand this was challenging. What do you think could have been done differently to improve this situation?",
            "longed_for": "That's a great vision for improvement! What would need to change to make this possible?"
        }
        return fallback_responses.get(current_step, "Thanks for sharing that! Could you tell me more about it?")
    
    def _is_inappropriate_content(self, message: str) -> bool:
        """Check if message contains inappropriate content"""
        inappropriate_keywords = [
            # Drugs and illegal substances
            'drug', 'drugs', 'smuggle', 'smuggling', 'cocaine', 'heroin', 'marijuana', 'weed',
            
            # Violence and weapons
            'violence', 'death', 'kill', 'murder', 'weapon', 'gun', 'bomb', 'attack', 'hijack', 'hijacking',
            
            # Sexual content and trafficking
            'sex', 'sexual', 'trafficking', 'prostitution', 'porn', 'pornography', 'rape', 'abuse',
            
            # Political conflicts
            'hamas', 'israel', 'palestine', 'war', 'terrorism', 'terrorist',
            
            # Political topics
            'political', 'election', 'vote', 'government', 'president', 'politics',
            
            # Illegal activities
            'illegal', 'crime', 'criminal', 'jail', 'prison', 'steal', 'theft', 'fraud',
            
            # Money laundering and illegal financial activities
            'money laundering', 'laundering', 'rich', 'wealth', 'profit', 'earn money', 'make money',
            
            # Human trafficking and exploitation
            'traffic', 'exploit', 'exploitation', 'slave', 'slavery', 'kidnap', 'kidnapping'
        ]
        
        message_lower = message.lower()
        
        # Check for exact matches and partial matches
        for keyword in inappropriate_keywords:
            if keyword in message_lower:
                return True
        
        # Check for combinations that might be inappropriate
        inappropriate_combinations = [
            'sex trafficking', 'human trafficking', 'drug smuggling', 'money laundering',
            'make money', 'earn money', 'get rich', 'be rich', 'will be rich',
            'more women', 'more men'
        ]
        
        for combination in inappropriate_combinations:
            if combination in message_lower:
                return True
        
        return False
    
    def _get_redirect_response(self, current_step: str) -> str:
        """Get a polite redirect response for inappropriate content"""
        redirect_responses = {
            "liked": "Hi there! Let's focus on our retrospective. What did you like about this sprint? What went well that you'd like to continue?",
            "learned": "Hey! Let's stay focused on our sprint retrospective. What did you learn during this sprint? What new insights or knowledge did you gain?",
            "lacked": "Hi! I'd like to keep our discussion focused on the sprint. What challenges did you face? What didn't go well that we could improve?",
            "longed_for": "Hello! Let's concentrate on our retrospective. What would you like to see happen differently in future sprints? What improvements do you hope for?"
        }
        return redirect_responses.get(current_step, "Hi! Let's focus on our retrospective discussion. How can I help you reflect on your sprint?")
    
    async def analyze_retrospective_patterns(
        self, 
        responses: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze patterns across retrospective responses"""
        
        if not responses:
            return {"patterns": [], "insights": [], "recommendations": []}
        
        # Group responses by 4Ls category
        categories = {"liked": [], "learned": [], "lacked": [], "longed_for": []}
        
        for response in responses:
            for category in categories:
                if response.get(category):
                    categories[category].append(response[category])
        
        # Generate analysis prompt
        analysis_prompt = f"""
        Analyze these retrospective responses and provide insights:
        
        Liked: {categories['liked']}
        Learned: {categories['learned']}
        Lacked: {categories['lacked']}
        Longed For: {categories['longed_for']}
        
        Please provide:
        1. Key patterns and themes
        2. Actionable insights
        3. Specific recommendations for improvement
        
        Keep it concise and actionable.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert agile coach analyzing retrospective data."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=300,
                temperature=0.5
            )
            
            analysis = response.choices[0].message.content.strip()
            
            return {
                "analysis": analysis,
                "patterns": self._extract_patterns(categories),
                "insights": self._extract_insights(categories),
                "recommendations": self._extract_recommendations(categories)
            }
            
        except Exception as e:
            return {
                "analysis": "Unable to analyze patterns at this time.",
                "patterns": [],
                "insights": [],
                "recommendations": []
            }
    
    def _extract_patterns(self, categories: Dict) -> List[str]:
        """Extract patterns from categorized responses"""
        patterns = []
        
        # Simple pattern detection
        for category, responses in categories.items():
            if len(responses) > 1:
                # Look for common themes (simplified)
                if any("communication" in r.lower() for r in responses):
                    patterns.append(f"Communication themes in {category}")
                if any("process" in r.lower() for r in responses):
                    patterns.append(f"Process-related feedback in {category}")
        
        return patterns
    
    def _extract_insights(self, categories: Dict) -> List[str]:
        """Extract insights from categorized responses"""
        insights = []
        
        # Count responses per category
        for category, responses in categories.items():
            if responses:
                insights.append(f"Strong {category} feedback with {len(responses)} responses")
        
        return insights
    
    def _extract_recommendations(self, categories: Dict) -> List[str]:
        """Extract recommendations from categorized responses"""
        recommendations = []
        
        # Generate basic recommendations based on categories
        if categories["lacked"]:
            recommendations.append("Address the challenges identified in the 'Lacked' category")
        if categories["longed_for"]:
            recommendations.append("Consider implementing improvements from 'Longed For' feedback")
        if categories["liked"]:
            recommendations.append("Continue practices identified in 'Liked' category")
        
        return recommendations
    
    async def generate_action_items(
        self, 
        retrospective_data: Dict
    ) -> List[Dict[str, Any]]:
        """Generate action items from retrospective data"""
        
        prompt = f"""
        Based on this retrospective data, suggest 3-5 specific, actionable action items:
        
        Liked: {retrospective_data.get('liked', [])}
        Learned: {retrospective_data.get('learned', [])}
        Lacked: {retrospective_data.get('lacked', [])}
        Longed For: {retrospective_data.get('longed_for', [])}
        
        For each action item, provide:
        - Title (clear and specific)
        - Description (what needs to be done)
        - Priority (High/Medium/Low)
        - Suggested assignee role
        
        Format as JSON array.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert agile coach creating actionable items from retrospectives."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            # Parse JSON response
            content = response.choices[0].message.content.strip()
            # Extract JSON from response (handle cases where AI adds extra text)
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                action_items = json.loads(json_str)
                return action_items
            
        except Exception as e:
            print(f"Error generating action items: {e}")
        
        # Fallback action items
        return [
            {
                "title": "Review and address challenges",
                "description": "Review the challenges identified in the retrospective and create a plan to address them",
                "priority": "High",
                "suggested_role": "scrum-master"
            },
            {
                "title": "Implement improvement suggestions",
                "description": "Work on implementing the improvements suggested in the 'Longed For' category",
                "priority": "Medium",
                "suggested_role": "product-owner"
            }
        ]
