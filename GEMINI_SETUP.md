# 🤖 Enhanced YodaAI with Gemini API Setup

## Overview

YodaAI has been enhanced to use **Gemini API** for intelligent content filtering and contextual responses, replacing hardcoded filtering with AI-powered analysis.

## Key Improvements

### ✅ **AI-Powered Content Filtering**
- **Before**: Hardcoded keyword filtering
- **After**: Gemini API analyzes content appropriateness for retrospective context
- **Benefits**: More intelligent, context-aware filtering

### ✅ **Project Context Integration**
- **Before**: Generic responses
- **After**: Responses reference team information, roles, and project context
- **Benefits**: More relevant and personalized responses

### ✅ **Document Reference System**
- **Before**: No document integration
- **After**: AI references uploaded PDFs and documents in responses
- **Benefits**: Contextual responses based on actual project materials

### ✅ **Disciplined Agile Integration**
- **Before**: No framework integration
- **After**: AI applies Disciplined Agile principles and practices
- **Benefits**: Professional, framework-based guidance

### ✅ **Dynamic Responses**
- **Before**: Hardcoded conversation patterns
- **After**: AI generates contextual, natural responses
- **Benefits**: More engaging and relevant conversations

## Setup Instructions

### 1. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 2. Configure Environment

Add your Gemini API key to your environment:

```bash
# Option 1: Environment variable
export GEMINI_API_KEY="your_gemini_api_key_here"

# Option 2: .env file
echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env
```

### 3. Install Required Dependencies

```bash
pip install google-generativeai
```

### 4. Update Configuration

The configuration is already updated in `app/core/config.py`:

```python
# Gemini
GEMINI_API_KEY: Optional[str] = None
```

## How It Works

### Content Filtering Process

1. **User Input**: User sends a message
2. **AI Analysis**: Gemini API analyzes content appropriateness
3. **Context Check**: Considers project context and discipline reference
4. **Response**: Either generates contextual response or polite redirect

### Response Generation Process

1. **Context Gathering**: Collects team info, project context, uploaded documents
2. **Discipline Reference**: Loads Disciplined Agile framework content
3. **AI Generation**: Gemini generates contextual response
4. **Integration**: Response references project materials and DA principles

## Example Improvements

### Content Filtering
```
Input: "sex trafficking"
Before: Hardcoded keyword match → redirect
After:  AI analyzes context → "Let's focus on our retrospective discussion..."
```

### Contextual Responses
```
Input: "Our team worked well"
Before: Generic response
After:  "Thanks for sharing! Given your context as Frontend Developer in the React Team, what made this collaboration particularly effective?"
```

### Document Integration
```
Input: "We learned about new technologies"
Before: Generic follow-up
After:  "Excellent! Based on your uploaded architecture documents, which specific technologies from the tech stack made the biggest impact?"
```

## Files Modified

- `app/core/config.py` - Added Gemini API configuration
- `app/services/enhanced_ai_service.py` - New AI service with Gemini integration
- `app/services/ai_chat_service.py` - Updated to use enhanced service
- `yodaai-enhanced.html` - Removed hardcoded filtering
- `disciplined_agile_scrape.md` - Discipline reference file

## Testing

The system has been tested with:
- ✅ Content appropriateness detection
- ✅ Project context integration
- ✅ Document reference system
- ✅ Disciplined Agile framework integration
- ✅ Dynamic response generation

## Benefits

1. **Intelligent Filtering**: AI understands context, not just keywords
2. **Personalized Responses**: References actual project and team information
3. **Professional Guidance**: Applies Disciplined Agile principles
4. **Document Integration**: Uses uploaded materials for context
5. **Natural Conversations**: Dynamic, contextual responses
6. **No Hardcoding**: Flexible, AI-driven system

## Next Steps

1. Set your `GEMINI_API_KEY` environment variable
2. Install `google-generativeai` package
3. Restart the application
4. Test with inappropriate content to see AI filtering
5. Upload project documents to see contextual responses

The enhanced YodaAI now provides intelligent, contextual, and professional retrospective facilitation using AI-powered analysis and Disciplined Agile principles!
