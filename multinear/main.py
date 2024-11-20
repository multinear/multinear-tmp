from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .api.router import init_api, api_router


# Initialize API
init_api()

# Create FastAPI app with custom docs URLs
app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

# Serve frontend
frontend_path = Path(__file__).parent.parent / "multinear" / "frontend" / "build"
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
