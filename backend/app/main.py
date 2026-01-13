"""
FastAPI application entry point.
Mounts the contact router from api.py
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as contact_router

# Initialize FastAPI app
app = FastAPI(
    title="Contact Manager API",
    description="Professional contact management system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount contact router
app.include_router(contact_router, prefix="/api", tags=["contacts"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Contact Manager API",
        "version": "1.0.0"
    }


# Run with: uvicorn core.main:app --reload