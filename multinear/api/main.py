from fastapi import FastAPI, BackgroundTasks, HTTPException, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from time import sleep
import uuid
import yaml
from typing import Optional, Dict, List
from pathlib import Path


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

# Get the path to projects.yaml
current_file = Path(__file__)
project_root = current_file.parent.parent

# Read project configuration
with open(project_root / "projects.yaml", "r") as f:
    config = yaml.safe_load(f)

# Build projects dictionary with resolved paths
projects = {}
for project_id, project_data in config["projects"].items():
    projects[project_id] = {
        **project_data,
        "folder": str(Path(project_data["folder"]).expanduser().resolve())
    }

print(projects)

# Initialize job status using the projects config
job_status = {project_id: {} for project_id in projects}

def background_job(project_id: str, job_id: str):
    """Simulate a long-running task"""
    job_status[project_id][job_id] = "running"
    # Simulate work
    for i in range(20):
        sleep(1)
        job_status[project_id][job_id] = f"running {i}"
    job_status[project_id][job_id] = "completed"

# Schemas
class Project(BaseModel):
    id: str
    name: str
    description: str

class ProjectList(BaseModel):
    projects: List[Project]

class JobResponse(BaseModel):
    project_id: str
    job_id: str
    status: str
    details: Optional[Dict] = None

class JobStatusRequest(BaseModel):
    project_id: str
    job_id: str

class StartJobRequest(BaseModel):
    project_id: str

# Create API router
api_router = APIRouter(prefix="/api")

# Move all endpoints to use api_router instead of app
@api_router.get("/projects", response_model=ProjectList)
async def get_projects():
    projects_list = [
        Project(id=pid, name=pdata["name"], description=pdata["description"])
        for pid, pdata in projects.items()
    ]
    return ProjectList(projects=projects_list)

@api_router.post("/start", response_model=JobResponse)
async def start_job(request: StartJobRequest, background_tasks: BackgroundTasks):
    if request.project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    job_id = str(uuid.uuid4())
    background_tasks.add_task(background_job, request.project_id, job_id)
    return JobResponse(
        project_id=request.project_id,
        job_id=job_id,
        status="started"
    )

@api_router.post("/status", response_model=JobResponse)
async def get_job_status(request: JobStatusRequest):
    if request.project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    status = job_status[request.project_id].get(request.job_id, "not_found")
    details = {"progress": status} if status.startswith("running") else None
    return JobResponse(
        project_id=request.project_id,
        job_id=request.job_id,
        status=status,
        details=details
    )

# Include API router
app.include_router(api_router)

# Serve frontend
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")
