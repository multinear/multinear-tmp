from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .api.router import init_api, api_router


# Initialize the API and database
init_api()

# Create the FastAPI application with custom documentation URLs
app = FastAPI(
    docs_url="/api/docs",           # Swagger UI
    redoc_url="/api/redoc",         # Redoc
    openapi_url="/api/openapi.json" # OpenAPI JSON schema
)

# Add CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow all origins (update in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router with all endpoints
app.include_router(api_router)

# Serve the frontend static files (Svelte app)
frontend_path = Path(__file__).parent.parent / "multinear" / "frontend" / "build"
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
