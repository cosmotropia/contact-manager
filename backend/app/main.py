"""
FastAPI application entry point.
Mounts the contact router from api.py
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as contact_router
import os

# Initialize FastAPI app
app = FastAPI(
    title="Contact Manager API",
    description="Professional contact management system",
    version="1.0.0"
)

# CORS middleware
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://contact-manager-frontend.onrender.com",
        FRONTEND_URL,
    ],
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