# Vercel serverless function handler for LieLens API
import os
import json
import requests
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import re
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LieLens API",
    description="AI-powered misinformation detection and cognitive bias coaching",
    version="1.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo/development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request and Response Models
class AnalysisRequest(BaseModel):
    content: str = Field(..., min_length=10, max_length=10000, description="URL or text content to analyze")
    content_type: str = Field(default="auto", description="'url', 'text', or 'auto' to detect")
    user_id: Optional[str] = Field(None, description="Optional user identifier for analytics")

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# Demo analysis generator for Vercel deployment
def get_demo_analysis(content: str) -> Dict[str, Any]:
    """Generate demo analysis when Gemini API is not available"""
    content_length = len(content)
    has_emotional_words = bool(re.search(r'breaking|shocking|secret|exclusive|banned|hidden|urgent', content, re.I))
    has_all_caps = bool(re.search(r'[A-Z]{4,}', content))
    
    # Calculate risk based on content characteristics
    risk_score = 30  # Base score
    if has_emotional_words:
        risk_score += 25
    if has_all_caps:
        risk_score += 20
    if '!' in content:
        risk_score += 10
    if content_length < 100:
        risk_score -= 10
    
    risk_level = 'HIGH' if risk_score > 70 else 'MEDIUM' if risk_score > 50 else 'LOW'
    credibility = 'QUESTIONABLE' if risk_score > 50 else 'RELIABLE'
    
    return {
        "analysis_summary": {
            "risk_level": risk_level,
            "risk_score": min(risk_score, 95),
            "primary_concern": "Content uses emotional manipulation tactics" if has_emotional_words else "Content appears relatively neutral",
            "credibility_rating": credibility
        },
        "detected_tactics": [
            {
                "tactic_name": "Emotional Manipulation" if has_emotional_words else "Demo Analysis",
                "description": "Uses strong emotional language to bypass critical thinking" if has_emotional_words else "Demonstration of analysis capabilities",
                "example_from_content": content[:100] + "..." if len(content) > 100 else content,
                "manipulation_type": "EMOTIONAL"
            }
        ] if has_emotional_words else [
            {
                "tactic_name": "Demo Mode Active",
                "description": "This is a demonstration response showing system capabilities",
                "example_from_content": "Sample analysis",
                "manipulation_type": "LOGICAL"
            }
        ],
        "cognitive_biases": [
            {
                "bias_name": "Fear of Missing Out (FOMO)",
                "explanation": "The tendency to feel anxiety about missing beneficial opportunities",
                "how_its_exploited": "Content suggests exclusive or time-limited information",
                "resistance_tip": "Ask yourself: What's the real urgency? Can I verify this independently?"
            }
        ],
        "fact_check_flags": [
            {
                "claim": "Claims require verification",
                "flag_reason": "Vague or unsupported claims detected",
                "verification_suggestion": "Look for peer-reviewed studies and credible sources"
            }
        ] if has_emotional_words else [],
        "educational_insights": {
            "why_convincing": "Uses emotional triggers to create trust and urgency" if has_emotional_words else "Content appears straightforward",
            "target_audience": "People seeking exclusive information or solutions",
            "psychological_appeal": "Combines fear, hope, and exclusivity" if has_emotional_words else "Neutral presentation",
            "critical_questions": [
                "What evidence supports these claims?",
                "Who are the sources cited?",
                "What might be the motivation behind this content?",
                "Are there alternative explanations?"
            ],
            "verification_steps": [
                "Search for peer-reviewed research on this topic",
                "Check multiple reputable sources",
                "Look for expert opinions from relevant fields",
                "Consider potential conflicts of interest"
            ]
        },
        "recommendations": {
            "immediate_action": "Verify claims through multiple credible sources" if risk_score > 50 else "Proceed with normal fact-checking",
            "further_research": [
                "Search scientific databases",
                "Check fact-checking websites",
                "Consult domain experts"
            ],
            "share_decision": "SHARE_WITH_CONTEXT" if risk_score < 70 else "AVOID_SHARING",
            "learning_opportunity": "Practice identifying emotional manipulation in content"
        },
        "confidence_metrics": {
            "analysis_confidence": 75,
            "data_completeness": 60,
            "context_availability": "PARTIAL"
        },
        "metadata": {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "model_used": "demo-mode-vercel",
            "content_length": content_length,
            "source_type": "text"
        }
    }

# API Endpoints
@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy - demo mode active",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0-vercel"
    )

@app.post("/analyze")
async def analyze_content(request: AnalysisRequest):
    """Main analysis endpoint - demo mode for Vercel deployment"""
    try:
        content = request.content.strip()
        
        # Generate demo analysis
        logger.info(f"Analyzing content in demo mode ({len(content)} chars)")
        analysis_result = get_demo_analysis(content)
        
        logger.info("Demo analysis completed successfully")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Unexpected error in analyze_content: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/demo")
async def get_demo_analysis_endpoint():
    """Get a demo analysis for testing frontend"""
    demo_content = """
    BREAKING: Scientists SHOCKED by this simple trick that Big Pharma HATES! 
    They don't want you to know this one secret that could save your life. 
    Thousands of people are already using this, but the mainstream media won't report it. 
    Act fast - this information might be taken down soon!
    """
    
    analysis = get_demo_analysis(demo_content)
    return analysis

# Vercel handler
handler = app