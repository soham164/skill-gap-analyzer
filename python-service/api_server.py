"""
FastAPI Server for Skill Gap Analyzer
RESTful API with advanced endpoints for skill gap analysis
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json
import io
import pandas as pd
from datetime import datetime
import hashlib
import redis
import asyncio
from contextlib import asynccontextmanager
import logging

# Import our modules
from data_processor import DataProcessor
from skill_matcher import SkillMatcher, MatchingStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class SkillAnalysisRequest(BaseModel):
    resume_text: str = Field(..., description="Resume text content")
    job_text: str = Field(..., description="Job description text")
    strategy: str = Field(default="hybrid", description="Matching strategy to use")
    detailed: bool = Field(default=False, description="Return detailed analysis")

class SkillMatchResponse(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    additional_skills: List[str]
    match_percentage: float
    total_job_skills: int
    total_resume_skills: int
    recommendations: Optional[Dict] = None

class BatchAnalysisRequest(BaseModel):
    job_descriptions: List[Dict[str, str]]  # List of {id, title, description}
    strategy: str = Field(default="hybrid")

class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: bool
    timestamp: str

# Initialize components globally
data_processor = None
skill_matcher = None
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown
    """
    # Startup
    global data_processor, skill_matcher, redis_client
    
    logger.info("Starting Skill Gap Analyzer API...")
    
    # Initialize data processor and skill matcher
    data_processor = DataProcessor()
    skill_matcher = SkillMatcher(data_processor)
    
    # Initialize Redis for caching (optional)
    try:
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        redis_client.ping()
        logger.info("Redis cache connected")
    except:
        redis_client = None
        logger.warning("Redis not available - caching disabled")
    
    logger.info("API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    if redis_client:
        redis_client.close()

# Initialize FastAPI app
app = FastAPI(
    title="AI Skill Gap Analyzer API",
    description="Advanced API for analyzing skill gaps between resumes and job descriptions",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility functions
def get_cache_key(resume_text: str, job_text: str, strategy: str) -> str:
    """Generate cache key for analysis results"""
    content = f"{resume_text}:{job_text}:{strategy}"
    return hashlib.md5(content.encode()).hexdigest()

async def cache_result(key: str, result: dict, expire: int = 3600):
    """Cache analysis result in Redis"""
    if redis_client:
        try:
            redis_client.setex(key, expire, json.dumps(result))
        except:
            pass

async def get_cached_result(key: str) -> Optional[dict]:
    """Get cached result from Redis"""
    if redis_client:
        try:
            result = redis_client.get(key)
            if result:
                return json.loads(result)
        except:
            pass
    return None

# API Endpoints

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        models_loaded=skill_matcher is not None,
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check endpoint"""
    models_loaded = skill_matcher is not None and data_processor is not None
    
    if not models_loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        models_loaded=models_loaded,
        timestamp=datetime.utcnow().isoformat()
    )

@app.post("/api/skill-gap/analyze", response_model=SkillMatchResponse)
async def analyze_skill_gap(
    file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    job_text: str = Form(...),
    strategy: str = Form("hybrid"),
    detailed: bool = Form(False),
    use_cache: bool = Form(True)
):
    """
    Analyze skill gap between resume and job description
    
    Args:
        file: Resume PDF file (optional)
        resume_text: Resume text (alternative to file)
        job_text: Job description text
        strategy: Matching strategy (exact, fuzzy, semantic, contextual, hybrid)
        detailed: Return detailed analysis with confidence scores
        use_cache: Use cached results if available
    """
    
    # Extract resume text
    if file:
        pdf_bytes = await file.read()
        resume_content = data_processor.extract_text_from_pdf(pdf_bytes=pdf_bytes)
        if not resume_content:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
    elif resume_text:
        resume_content = resume_text
    else:
        raise HTTPException(status_code=400, detail="Either file or resume_text must be provided")
    
    # Check cache
    if use_cache:
        cache_key = get_cache_key(resume_content, job_text, strategy)
        cached = await get_cached_result(cache_key)
        if cached:
            logger.info("Returning cached result")
            return JSONResponse(content=cached)
    
    # Validate strategy
    try:
        strategy_enum = MatchingStrategy(strategy.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy. Must be one of: {[s.value for s in MatchingStrategy]}"
        )
    
    # Perform analysis
    try:
        result = skill_matcher.analyze_skill_gap(
            resume_content,
            job_text,
            detailed=detailed
        )
        
        # Add recommendations for missing skills
        if not detailed and result['missing_skills']:
            result['recommendations'] = skill_matcher.get_skill_recommendations(
                result['missing_skills'][:5]  # Top 5 missing skills
            )
        
        # Cache result
        if use_cache:
            await cache_result(cache_key, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/skill-gap/analyze-json")
async def analyze_skill_gap_json(request: SkillAnalysisRequest):
    """
    Analyze skill gap using JSON request body
    
    Args:
        request: SkillAnalysisRequest with resume and job text
    """
    try:
        strategy_enum = MatchingStrategy(request.strategy.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy. Must be one of: {[s.value for s in MatchingStrategy]}"
        )
    
    result = skill_matcher.analyze_skill_gap(
        request.resume_text,
        request.job_text,
        detailed=request.detailed
    )
    
    if not request.detailed and result.get('missing_skills'):
        result['recommendations'] = skill_matcher.get_skill_recommendations(
            result['missing_skills'][:5]
        )
    
    return result

@app.post("/api/skill-gap/batch-analyze")
async def batch_analyze(
    file: UploadFile = File(...),
    batch_request: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Batch analyze a resume against multiple job descriptions
    
    Args:
        file: Resume PDF file
        batch_request: JSON string with job descriptions
    """
    # Parse batch request
    try:
        batch_data = json.loads(batch_request)
        job_descriptions = batch_data.get('job_descriptions', [])
        strategy = batch_data.get('strategy', 'hybrid')
    except:
        raise HTTPException(status_code=400, detail="Invalid batch request format")
    
    if not job_descriptions:
        raise HTTPException(status_code=400, detail="No job descriptions provided")
    
    # Extract resume text
    pdf_bytes = await file.read()
    resume_text = data_processor.extract_text_from_pdf(pdf_bytes=pdf_bytes)
    
    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")
    
    # Analyze against each job description
    results = []
    for job in job_descriptions:
        try:
            analysis = skill_matcher.analyze_skill_gap(
                resume_text,
                job.get('description', ''),
                detailed=False
            )
            
            results.append({
                'job_id': job.get('id'),
                'job_title': job.get('title'),
                'match_percentage': analysis['match_percentage'],
                'matched_skills': len(analysis['matched_skills']),
                'missing_skills': len(analysis['missing_skills']),
                'top_missing': analysis['missing_skills'][:3]
            })
        except Exception as e:
            logger.error(f"Error analyzing job {job.get('id')}: {str(e)}")
            results.append({
                'job_id': job.get('id'),
                'job_title': job.get('title'),
                'error': str(e)
            })
    
    # Sort by match percentage
    results.sort(key=lambda x: x.get('match_percentage', 0), reverse=True)
    
    return {
        'total_jobs': len(job_descriptions),
        'analyzed': len([r for r in results if 'error' not in r]),
        'results': results
    }

@app.get("/api/skills/list")
async def list_skills(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search term")
):
    """
    List available skills in the database
    
    Args:
        category: Optional category filter
        search: Optional search term
    """
    skills = data_processor.canonical_skills.copy()
    
    # Filter by category
    if category:
        skills = [s for s in skills if data_processor.get_skill_category(s) == category.lower()]
    
    # Search filter
    if search:
        search_lower = search.lower()
        skills = [s for s in skills if search_lower in s.lower()]
    
    # Group by category
    categorized = {}
    for skill in skills:
        cat = data_processor.get_skill_category(skill)
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(skill)
    
    return {
        'total': len(skills),
        'categories': list(categorized.keys()),
        'skills': categorized
    }

@app.get("/api/skills/categories")
async def get_categories():
    """Get all skill categories"""
    return {
        'categories': list(data_processor.skills_db.keys()),
        'count': len(data_processor.skills_db)
    }

@app.get("/api/skills/{skill}/info")
async def get_skill_info(skill: str):
    """
    Get detailed information about a specific skill
    
    Args:
        skill: Skill name
    """
    skill_lower = skill.lower()
    
    if skill_lower not in data_processor.canonical_skills:
        # Try to find similar skill
        similar = [s for s in data_processor.canonical_skills if skill_lower in s or s in skill_lower]
        if not similar:
            raise HTTPException(status_code=404, detail=f"Skill '{skill}' not found")
        skill_lower = similar[0]
    
    return {
        'skill': skill_lower,
        'category': data_processor.get_skill_category(skill_lower),
        'related_skills': data_processor.get_related_skills(skill_lower, limit=10),
        'synonyms': data_processor.skill_synonyms.get(skill_lower, []),
        'recommendations': data_processor.recommendations.get(skill_lower, {})
    }

@app.post("/api/skills/extract")
async def extract_skills(
    text: str = Form(...),
    strategy: str = Form("hybrid")
):
    """
    Extract skills from any text
    
    Args:
        text: Text to extract skills from
        strategy: Matching strategy to use
    """
    try:
        strategy_enum = MatchingStrategy(strategy.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid strategy. Must be one of: {[s.value for s in MatchingStrategy]}"
        )
    
    # Get detailed matches
    matches = skill_matcher.match_skills_detailed(text, strategy_enum)
    
    # Format response
    skills_by_confidence = {}
    for match in matches:
        confidence_level = "high" if match.confidence > 0.8 else "medium" if match.confidence > 0.5 else "low"
        if confidence_level not in skills_by_confidence:
            skills_by_confidence[confidence_level] = []
        
        skills_by_confidence[confidence_level].append({
            'skill': match.skill,
            'confidence': round(match.confidence, 3),
            'category': match.category,
            'method': match.method
        })
    
    return {
        'total_skills': len(matches),
        'skills': [m.skill for m in matches],
        'detailed': skills_by_confidence
    }

@app.get("/api/export/skills-database")
async def export_skills_database(format: str = Query("csv", pattern="^(csv|json)$")):
    """
    Export the skills database
    
    Args:
        format: Export format (csv or json)
    """
    if format == "json":
        data = {
            'skills': data_processor.canonical_skills,
            'categories': data_processor.skills_db,
            'synonyms': data_processor.skill_synonyms,
            'total': len(data_processor.canonical_skills)
        }
        return JSONResponse(content=data)
    
    else:  # CSV
        # Create DataFrame
        skills_data = []
        for skill in data_processor.canonical_skills:
            skills_data.append({
                'skill': skill,
                'category': data_processor.get_skill_category(skill),
                'synonyms': ', '.join(data_processor.skill_synonyms.get(skill, []))
            })
        
        df = pd.DataFrame(skills_data)
        
        # Convert to CSV
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        
        return StreamingResponse(
            io.BytesIO(stream.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=skills_database.csv"}
        )

@app.post("/api/recommendations/generate")
async def generate_learning_path(
    skills: List[str] = Form(...),
    current_level: str = Form("beginner"),
    time_available: str = Form("3-6 months")
):
    """
    Generate a personalized learning path for given skills
    
    Args:
        skills: List of skills to learn
        current_level: Current skill level (beginner, intermediate, advanced)
        time_available: Time available for learning
    """
    if not skills:
        raise HTTPException(status_code=400, detail="No skills provided")
    
    learning_path = []
    total_time_estimate = 0
    
    for skill in skills:
        skill_lower = skill.lower()
        
        # Get skill info
        if skill_lower in data_processor.canonical_skills:
            recommendation = data_processor.recommendations.get(skill_lower, {})
            category = data_processor.get_skill_category(skill_lower)
            related = data_processor.get_related_skills(skill_lower, limit=3)
            
            # Estimate time based on difficulty and current level
            difficulty = recommendation.get('difficulty', 'intermediate')
            base_time = recommendation.get('time_estimate', '2-3 months')
            
            # Parse time estimate (simplified)
            if 'month' in base_time:
                months = 3  # Default estimate
                if '1-2' in base_time:
                    months = 1.5
                elif '2-3' in base_time:
                    months = 2.5
                elif '3-4' in base_time:
                    months = 3.5
                elif '4-6' in base_time:
                    months = 5
                elif '3-6' in base_time:
                    months = 4.5
                
                # Adjust based on current level
                if current_level == "intermediate" and difficulty == "beginner":
                    months *= 0.5
                elif current_level == "advanced":
                    months *= 0.3
                elif current_level == "beginner" and difficulty == "advanced":
                    months *= 1.5
                
                total_time_estimate += months
            
            learning_path.append({
                'skill': skill_lower,
                'category': category,
                'difficulty': difficulty,
                'estimated_time': base_time,
                'resources': recommendation.get('courses', []),
                'related_skills': related,
                'priority': 'high' if skill in skills[:3] else 'medium'
            })
    
    # Sort by category and difficulty
    learning_path.sort(key=lambda x: (x['category'], x['difficulty']))
    
    return {
        'total_skills': len(learning_path),
        'estimated_total_time': f"{total_time_estimate:.1f} months",
        'time_available': time_available,
        'current_level': current_level,
        'learning_path': learning_path,
        'recommendation': "Focus on high-priority skills first and learn related skills together for better retention."
    }

@app.get("/api/stats")
async def get_statistics():
    """Get API usage statistics and system information"""
    return {
        'system': {
            'version': '2.0.0',
            'total_skills': len(data_processor.canonical_skills),
            'total_categories': len(data_processor.skills_db),
            'total_recommendations': len(data_processor.recommendations),
            'cache_enabled': redis_client is not None
        },
        'models': {
            'nlp_model': 'en_core_web_sm',
            'embedding_model': 'all-MiniLM-L6-v2',
            'matching_strategies': [s.value for s in MatchingStrategy]
        }
    }

@app.post("/api/feedback")
async def submit_feedback(
    skill: str = Form(...),
    feedback_type: str = Form(...),  # missing_skill, wrong_category, other
    details: str = Form(None)
):
    """
    Submit feedback about skill detection or recommendations
    
    Args:
        skill: Skill name
        feedback_type: Type of feedback
        details: Additional details
    """
    # In production, this would save to a database
    feedback_data = {
        'skill': skill,
        'type': feedback_type,
        'details': details,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    logger.info(f"Feedback received: {feedback_data}")
    
    return {
        'status': 'success',
        'message': 'Thank you for your feedback. We will review and improve our system.',
        'feedback_id': hashlib.md5(str(feedback_data).encode()).hexdigest()[:8]
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': exc.detail,
            'status_code': exc.status_code,
            'timestamp': datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            'error': 'Internal server error',
            'status_code': 500,
            'timestamp': datetime.utcnow().isoformat()
        }
    )

# Main entry point
if __name__ == "_main_":
    import uvicorn
    
    # Configuration
    config = {
        'host': '0.0.0.0',
        'port': 8000,
        'reload': True,  # Set to False in production
        'workers': 1,    # Increase for production
        'log_level': 'info'
    }
    
    logger.info(f"Starting server with config: {config}")
    
    # Run server
    uvicorn.run(
        "api_server:app",
        host=config['host'],
        port=config['port'],
        reload=config['reload'],
        workers=config['workers'],
        log_level=config['log_level']
    )