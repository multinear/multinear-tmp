from fastapi import FastAPI, BackgroundTasks, HTTPException, APIRouter, Query, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from time import sleep
import uuid
import yaml
from typing import Optional, Dict, List
from pathlib import Path
from datetime import datetime, timedelta, timezone
import random
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from .run import run_experiment, ExperimentStatus
from .storage import init_db, get_db, db_context, ProjectModel, JobModel


init_db()

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

# Get the current working directory and load multinear.yaml
current_dir = Path.cwd()
project_root = current_dir.parent

# Read project configuration from local multinear.yaml
with open(current_dir / ".multinear" / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Create single project configuration
project_id = config["project"]["id"]
project_data = {
    "id": project_id,
    "name": config["project"]["name"],
    "description": config["project"]["description"],
    "folder": str(current_dir)
}

# Update project in database on startup
with db_context() as db:
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if project:
        # Update existing project details
        project.name = project_data["name"]
        project.description = project_data["description"]
        project.folder = project_data["folder"]
    else:
        # Add new project
        project = ProjectModel(
            id=project_id,
            name=project_data["name"],
            description=project_data["description"],
            folder=project_data["folder"]
        )
        db.add(project)
    db.commit()

# Update background_job to persist job to DB
def background_job(project_id: str, job_id: str):
    """Run the experiment for the given project"""
    with db_context() as db:
        try:
            project = db.query(ProjectModel).filter(ProjectModel.id == project_id).one()
            job = db.query(JobModel).filter(JobModel.id == job_id).one()  # Get existing job
            
            for update in run_experiment(project.to_dict(), job_id):
                # Update job status in DB
                job.status = update["status"]
                job.total_tasks = update.get("total", 0)
                job.current_task = update.get("current")
                job.details = update
                db.commit()
        except Exception as e:
            print(f"Error running experiment: {e}")
            db.rollback()
            # Update job status in DB
            job = db.query(JobModel).filter(JobModel.id == job_id).one()
            job.status = "failed"
            job.details = {"error": str(e)}
            db.commit()

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

@api_router.get("/projects", response_model=List[Project])
async def get_projects(db: Session = Depends(get_db)):
    projects = db.query(ProjectModel).all()
    return [
        Project(id=p.id, name=p.name, description=p.description)
        for p in projects
    ]

@api_router.post("/jobs/{project_id}", response_model=JobResponse)
async def create_job(project_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    job_id = str(uuid.uuid4())
    job = JobModel(id=job_id, project_id=project_id, status="started")
    db.add(job)
    db.commit()
    
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
async def get_job_status(project_id: str, job_id: str, db: Session = Depends(get_db)):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        job = db.query(JobModel).filter(JobModel.id == job_id, JobModel.project_id == project_id).one()
        details = job.details or {}  # details is already a dict
        
        return JobResponse(
            project_id=project_id,
            job_id=job_id,
            status=job.status,
            total_tasks=job.total_tasks,
            current_task=job.current_task,
            task_status_map=details.get("status_map", {}),
            details=details
        )
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Job not found")

def generate_fake_run(job_id: str, job_data: dict, created_at: datetime) -> dict:
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
    if isinstance(created_at, int):
        created_at = datetime.now() - timedelta(hours=random.randint(0, 23), 
                                                minutes=random.randint(0, 59))
    
    # Calculate score based on actual results if available
    if total > 0:
        score = (passed / total) * random.uniform(0.95, 1.05)  # Add some randomness
        score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
    else:
        score = random.uniform(0.75, 0.98)
    
    return {
        "id": job_id,
        "date": created_at.replace(tzinfo=timezone.utc).isoformat(),
        # "date": created_at.replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M %Z"),
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
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    if not db.query(ProjectModel).filter(ProjectModel.id == project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get recent jobs from database
    recent_jobs = (
        db.query(JobModel)
        .filter(JobModel.project_id == project_id)
        .order_by(JobModel.created_at.desc())  # Order by timestamp instead of id
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    runs = []
    for job in recent_jobs:
        job_data = job.details or {}
        run = generate_fake_run(job.id, job_data, job.created_at)
        runs.append(run)
    
    # If we have fewer than 5 runs from real data, add some fake ones
    while len(runs) < 5:
        fake_id = f"RUN-{str(len(runs) + 1).zfill(3)}"
        runs.append(generate_fake_run(fake_id, {}, len(runs)))
    
    # Sort runs by date, most recent first
    # runs.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d %H:%M"), reverse=True)
    
    return runs

# Include API router
app.include_router(api_router)

# Serve frontend
frontend_path = Path(__file__).parent.parent / "frontend" / "build"
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
