from fastapi import FastAPI, BackgroundTasks, HTTPException, APIRouter, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from time import sleep
import uuid
import yaml
from typing import Optional, Dict, List
from pathlib import Path
from datetime import datetime, timedelta
import random

from .run import run_experiment, ExperimentStatus


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

# print(projects)

# Initialize job status using the projects config
job_status = {project_id: {} for project_id in projects}

def background_job(project_id: str, job_id: str):
    """Run the experiment for the given project"""
    try:
        for update in run_experiment(projects[project_id]):
            job_status[project_id][job_id] = update
    except Exception as e:
        job_status[project_id][job_id] = {
            "status": "failed",
            "error": f"Job execution failed: {str(e)}"
        }

# Schemas
class Project(BaseModel):
    id: str
    name: str
    description: str

class JobResponse(BaseModel):
    project_id: str
    job_id: str
    status: str
    total_tasks: int
    current_task: Optional[int] = None
    task_status_map: Optional[Dict] = None
    details: Optional[Dict] = None

class RecentRun(BaseModel):
    id: str
    date: str
    revision: str
    model: str
    score: float
    totalTests: int
    pass_: int = Field(alias='pass')  # 'pass' is a Python keyword
    fail: int
    regression: int
    bookmarked: Optional[bool] = False
    noted: Optional[bool] = False

# Create API router
api_router = APIRouter(prefix="/api")

# Move all endpoints to use api_router instead of app
@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    projects_list = [
        Project(id=pid, name=pdata["name"], description=pdata["description"])
        for pid, pdata in projects.items()
    ]
    return projects_list

@api_router.post("/jobs/{project_id}", response_model=JobResponse)
async def create_job(project_id: str, background_tasks: BackgroundTasks):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    job_id = str(uuid.uuid4())
    background_tasks.add_task(background_job, project_id, job_id)
    return JobResponse(
        project_id=project_id,
        job_id=job_id,
        status="started",
        total_tasks=0,
        task_status_map={},
        details={}
    )

@api_router.get("/jobs/{project_id}/{job_id}/status", response_model=JobResponse)
async def get_job_status(project_id: str, job_id: str):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    job_state = job_status[project_id].get(job_id, "not_found")
    if job_state == "not_found":
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse(
        project_id=project_id,
        job_id=job_id,
        status=job_state["status"].value,
        total_tasks=job_state["total"],
        current_task=job_state.get("current", None),
        task_status_map=job_state.get("status_map", {}),
        details=job_state  # Include full job state
    )

def generate_fake_run(job_id: str, job_data: dict, days_ago: int = 0) -> dict:
    total = random.randint(450, 550)
    passed = int(total * random.uniform(0.75, 0.95))
    failed = int(total * random.uniform(0.03, 0.15))
    regression = total - passed - failed
    
    models = ["gpt4o", "sonnet-3.5", "gpt4o-mini", "haiku-3.5"]
    
    # Use actual job data where available
    status = job_data.get("status", "unknown")
    task_status_map = job_data.get("status_map", {})
    
    # Calculate actual stats if available
    if task_status_map:
        total = len(task_status_map)
        passed = sum(1 for status in task_status_map.values() if status == ExperimentStatus.COMPLETED)
        failed = sum(1 for status in task_status_map.values() if status == ExperimentStatus.FAILED)
        regression = total - passed - failed
    
    # Use actual timestamp if available, otherwise generate fake
    if "start_time" in job_data:
        date = datetime.fromisoformat(job_data["start_time"])
    else:
        date = datetime.now() - timedelta(days=days_ago, 
                                        hours=random.randint(0, 23), 
                                        minutes=random.randint(0, 59))
    
    # Calculate score based on actual results if available
    if total > 0:
        score = (passed / total) * random.uniform(0.95, 1.05)  # Add some randomness
        score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
    else:
        score = random.uniform(0.75, 0.98)
    
    return {
        "id": job_id,
        "date": date.strftime("%Y-%m-%d %H:%M"),
        "revision": job_data.get("revision", hex(random.randint(0, 16**8))[2:].zfill(8)),
        "model": job_data.get("model", random.choice(models)),
        "score": score,
        "totalTests": total,
        "pass": passed,
        "fail": failed,
        "regression": regression,
        "bookmarked": random.random() < 0.2,
        "noted": random.random() < 0.2
    }

@api_router.get("/runs/{project_id}", response_model=List[RecentRun])
async def get_recent_runs(
    project_id: str,
    limit: int = Query(5, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_jobs = job_status.get(project_id, {})
    runs = []
    for job_id, job_data in list(project_jobs.items())[offset:offset+limit]:
        if isinstance(job_data, dict):
            run = generate_fake_run(job_id, job_data)
            runs.append(run)
    
    # If we have fewer than 5 runs from real data, add some fake ones
    while len(runs) < 5:
        fake_id = f"RUN-{str(len(runs) + 1).zfill(3)}"
        runs.append(generate_fake_run(fake_id, {}, len(runs)))
    
    # Sort runs by date, most recent first
    runs.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d %H:%M"), reverse=True)
    
    return runs

# Include API router
app.include_router(api_router)

# Serve frontend
app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")
