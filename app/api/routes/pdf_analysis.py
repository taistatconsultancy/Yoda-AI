"""
PDF analysis and document processing routes
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.dependencies.auth import get_current_user
from app.models.user import User
import PyPDF2
import io
import openai
import os
from typing import Dict, Any

router = APIRouter()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and analyze PDF document"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read PDF content
        content = await file.read()
        
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in PDF")
        
        # Analyze with OpenAI
        analysis = await analyze_document_with_ai(text, file.filename)
        
        return {
            "filename": file.filename,
            "size": len(content),
            "analysis": analysis,
            "extracted_text": text[:1000] + "..." if len(text) > 1000 else text
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

async def analyze_document_with_ai(text: str, filename: str) -> Dict[str, Any]:
    """Analyze document content with OpenAI"""
    
    prompt = f"""
    Analyze the following document "{filename}" and provide:
    
    1. Key Topics and Themes
    2. Main Challenges Identified
    3. Success Factors Mentioned
    4. Action Items Suggested
    5. Retrospective Insights (how this relates to agile practices)
    6. Recommendations for Team Improvement
    
    Document Content:
    {text[:3000]}  # Limit to first 3000 characters
    
    Please provide a structured analysis that would be useful for a retrospective discussion.
    """
    
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant specialized in analyzing project documents for agile retrospectives. Provide actionable insights and recommendations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        analysis_text = response.choices[0].message.content
        
        # Parse the analysis into structured format
        return {
            "summary": analysis_text,
            "key_topics": extract_key_topics(analysis_text),
            "challenges": extract_challenges(analysis_text),
            "success_factors": extract_success_factors(analysis_text),
            "action_items": extract_action_items(analysis_text),
            "retrospective_insights": extract_retrospective_insights(analysis_text)
        }
        
    except Exception as e:
        return {
            "summary": f"Analysis failed: {str(e)}",
            "key_topics": [],
            "challenges": [],
            "success_factors": [],
            "action_items": [],
            "retrospective_insights": []
        }

def extract_key_topics(text: str) -> list:
    """Extract key topics from analysis"""
    # Simple extraction - in production, use more sophisticated NLP
    topics = []
    lines = text.split('\n')
    for line in lines:
        if 'topic' in line.lower() or 'theme' in line.lower():
            topics.append(line.strip())
    return topics[:5]  # Limit to 5 topics

def extract_challenges(text: str) -> list:
    """Extract challenges from analysis"""
    challenges = []
    lines = text.split('\n')
    for line in lines:
        if 'challenge' in line.lower() or 'problem' in line.lower() or 'issue' in line.lower():
            challenges.append(line.strip())
    return challenges[:5]

def extract_success_factors(text: str) -> list:
    """Extract success factors from analysis"""
    factors = []
    lines = text.split('\n')
    for line in lines:
        if 'success' in line.lower() or 'positive' in line.lower() or 'good' in line.lower():
            factors.append(line.strip())
    return factors[:5]

def extract_action_items(text: str) -> list:
    """Extract action items from analysis"""
    items = []
    lines = text.split('\n')
    for line in lines:
        if 'action' in line.lower() or 'recommend' in line.lower() or 'suggest' in line.lower():
            items.append(line.strip())
    return items[:5]

def extract_retrospective_insights(text: str) -> list:
    """Extract retrospective insights from analysis"""
    insights = []
    lines = text.split('\n')
    for line in lines:
        if 'retrospective' in line.lower() or 'agile' in line.lower() or 'sprint' in line.lower():
            insights.append(line.strip())
    return insights[:5]
