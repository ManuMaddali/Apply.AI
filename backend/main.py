from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routes
from routes.upload_resume import router as upload_router
from routes.scrape_jobs import router as scrape_router
from routes.generate_resumes import router as generate_router
from routes.batch_processing import router as batch_router

app = FastAPI(
    title="AI Resume Tailoring API",
    description="LangChain-powered AI Resume Tailoring with RAG, Diff Analysis, and Batch Processing",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Mount static files
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": [
            "LangChain RAG",
            "Advanced Diff Analysis", 
            "Session Management",
            "Vector Storage",
            "Batch Processing"
        ]
    }

# Include routers
app.include_router(upload_router, prefix="/api/resumes", tags=["resumes"])
app.include_router(scrape_router, prefix="/api/jobs", tags=["jobs"])
app.include_router(generate_router, prefix="/api/resumes", tags=["resumes"])
app.include_router(batch_router, prefix="/api/batch", tags=["batch"])

@app.get("/")
async def root():
    return {
        "message": "🚀 AI Resume Tailoring API with LangChain & Batch Processing",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "features": ["Single Mode", "Batch Mode", "RAG Enhancement", "Real-time Processing"]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port, reload=True) 