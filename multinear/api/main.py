from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from time import sleep
import uuid
import yaml
from typing import Optional, Dict, List
from pathlib import Path


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the path to config.yaml
current_file = Path(__file__)
project_root = current_file.parent.parent

# Read project configuration
with open(project_root / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

print(config)

# Modified to store jobs per project
job_status = {project_id: {} for project_id in config["projects"]}

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

# Get projects
@app.get("/projects", response_model=ProjectList)
async def get_projects():
    projects = [
        Project(id=pid, name=pdata["name"], description=pdata["description"])
        for pid, pdata in config["projects"].items()
    ]
    return ProjectList(projects=projects)

# Start a job
@app.post("/start", response_model=JobResponse)
async def start_job(request: StartJobRequest, background_tasks: BackgroundTasks):
    if request.project_id not in config["projects"]:
        raise HTTPException(status_code=404, detail="Project not found")
    
    job_id = str(uuid.uuid4())
    background_tasks.add_task(background_job, request.project_id, job_id)
    return JobResponse(
        project_id=request.project_id,
        job_id=job_id,
        status="started"
    )

# Get job status
@app.post("/status", response_model=JobResponse)
async def get_job_status(request: JobStatusRequest):
    if request.project_id not in config["projects"]:
        raise HTTPException(status_code=404, detail="Project not found")
    
    status = job_status[request.project_id].get(request.job_id, "not_found")
    details = {"progress": status} if status.startswith("running") else None
    return JobResponse(
        project_id=request.project_id,
        job_id=request.job_id,
        status=status,
        details=details
    )

# Serve frontend
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")
