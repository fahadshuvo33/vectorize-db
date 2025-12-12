# main.py


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, users
from app.core.config import settings

app = FastAPI(
    title="VectorizeDB API",
    description="Turn databases into AI-ready formats",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "VectorizeDB API",
        "version": "1.0.0",
        "message": "Welcome to VectorizeDB API",
        "docs": "/docs",
        "endpoints": {
            "health": "/",
            "api_docs": "/docs",
            "auth": "/api/v1/auth",
            "upload": "/api/v1/upload",
            "chat": "/api/v1/chat",
        },
    }


@app.get("/health")
async def health():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "VectorizeDB API",
        "version": "1.0.0",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
