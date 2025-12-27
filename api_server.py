"""
FastAPI server for Ethika Chat.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
from rag_system import RAGSystem
from advanced_curriculum_generator import AdvancedCurriculumGenerator
from prompt_based_generator import PromptBasedGenerator
import uvicorn
import os

app = FastAPI(title="Ethika Chat API", version="1.0.0")

# Enable CORS for React frontend
# Allow all origins in production (Railway), restrict in development
import os
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from React build (for production)
frontend_build_path = Path(__file__).parent / "frontend" / "build"
if frontend_build_path.exists():
    # Serve static files (JS, CSS, images, etc.)
    app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")
    
    # Serve React app for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Don't serve API routes as static files
        if full_path.startswith("api/") or full_path in ["search", "curriculum", "generate-from-prompt", "resources", "health"]:
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for all other routes (React Router)
        index_path = frontend_build_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        raise HTTPException(status_code=404, detail="Frontend not built")

# Initialize RAG system (lazy loading)
_rag_system = None
_curriculum_generator = None


def get_rag_system():
    """Lazy initialization of RAG system."""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
    return _rag_system


def get_curriculum_generator():
    """Lazy initialization of curriculum generator."""
    global _curriculum_generator
    if _curriculum_generator is None:
        _curriculum_generator = AdvancedCurriculumGenerator(get_rag_system())
    return _curriculum_generator


# Request/Response models
class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    institution: Optional[str] = None
    target_audience: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    resource_type: Optional[List[str]] = None


class CurriculumRequest(BaseModel):
    institution: str
    target_audience: List[str]
    topics: List[str]
    duration_hours: float = 2.0
    preferred_types: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    institution_context: Optional[str] = None
    use_advanced: bool = True


class PromptRequest(BaseModel):
    prompt: str
    max_tokens: int = 8192  # Increased default for complete workshops
    use_llm: bool = True  # Set to False to skip LLM and just return curated resources


@app.get("/api")
def api_root():
    """API root endpoint."""
    return {
        "message": "Ethika Chat API",
        "endpoints": {
            "/api/search": "POST - Search for resources",
            "/api/curriculum": "POST - Generate curriculum (legacy)",
            "/api/generate-from-prompt": "POST - Generate content from natural language prompt (ChatGPT-like)",
            "/api/resources": "GET - List all resources",
            "/api/health": "GET - Health check"
    }


@app.get("/api/health")
def health():
    """Health check endpoint."""
    try:
        # Just return healthy without initializing RAG system
        return {"status": "healthy", "message": "API server is running"}
    except Exception as e:
        # Even if there's an error, return a response (not 500)
        return {"status": "error", "message": str(e)}


@app.post("/api/search")
def search(request: SearchRequest):
    """
    Search for educational resources.
    
    Example:
    {
        "query": "machine learning activities",
        "limit": 5,
        "target_audience": ["elementary"],
        "tags": ["machine_learning"]
    }
    """
    try:
        rag = get_rag_system()
        results = rag.search(
            query=request.query,
            limit=request.limit,
            institution=request.institution,
            target_audience=request.target_audience,
            tags=request.tags,
            resource_type=request.resource_type
        )
        return {
            "query": request.query,
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/curriculum")
def generate_curriculum(request: CurriculumRequest):
    """
    Generate a customized curriculum.
    
    Example:
    {
        "institution": "MIT",
        "target_audience": ["middle_school"],
        "topics": ["machine_learning", "ethics"],
        "duration_hours": 3.0,
        "use_advanced": true
    }
    """
    try:
        if request.use_advanced:
            generator = get_curriculum_generator()
            curriculum = generator.generate_detailed_curriculum(
                institution=request.institution,
                target_audience=request.target_audience,
                topics=request.topics,
                duration_hours=request.duration_hours,
                preferred_types=request.preferred_types,
                learning_objectives=request.learning_objectives,
                institution_context=request.institution_context
            )
        else:
            rag = get_rag_system()
            curriculum = rag.generate_curriculum(
                institution=request.institution,
                target_audience=request.target_audience,
                topics=request.topics,
                duration_hours=request.duration_hours,
                preferred_types=request.preferred_types
            )
        
        return curriculum
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/resources")
def list_resources(limit: Optional[int] = None):
    """List all resources in the database."""
    try:
        rag = get_rag_system()
        resources = rag.get_all_resources(limit=limit)
        return {
            "count": len(resources),
            "resources": resources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-from-prompt")
def generate_from_prompt(request: PromptRequest):
    """
    Generate educational content from a natural language prompt.
    Like ChatGPT but specifically for your educational database.
    
    Example:
    {
        "prompt": "Create a 2-hour workshop on AI ethics for middle school students at MIT. Include interactive activities about bias in AI systems.",
        "num_resources": 10
    }
    """
    try:
        rag = get_rag_system()
        generator = PromptBasedGenerator(rag)
        
        result = generator.generate_from_prompt(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            use_llm=request.use_llm
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

