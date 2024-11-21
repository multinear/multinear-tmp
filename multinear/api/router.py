from fastapi import BackgroundTasks, HTTPException, APIRouter, Query
from typing import List
from pathlib import Path
import yaml
from datetime import timezone

from ..api.schemas import Project, JobDetails, RecentRun, FullRunDetails, TaskDetails
from ..engine.run import run_experiment
from ..engine.storage import init_db, ProjectModel, JobModel, TaskModel, TaskStatus


def init_api():
    init_db()

    # Get the current working directory and load multinear.yaml
    current_dir = Path.cwd()

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
    ProjectModel.save(
        id=project_id,
        name=project_data["name"],
        description=project_data["description"],
        folder=project_data["folder"]
    )


def background_job(project_id: str, job_id: str):
    """Run the experiment for the given project"""
    try:
        project = ProjectModel.find(project_id)
        job = JobModel.find(job_id)
        
        for update in run_experiment(project.to_dict(), job_id):
            # Add status map from TaskModel to the update
            update["status_map"] = TaskModel.get_status_map(job_id)
            
            # Update job status in DB
            job.update(
                status=update["status"],
                total_tasks=update.get("total", 0),
                current_task=update.get("current"),
                details=update
            )

        job.finish()
    except Exception as e:
        print(f"Error running experiment API: {e}")
        job = JobModel.find(job_id)
        job.update(
            status="failed",
            details={
                "error": str(e),
                "status_map": TaskModel.get_status_map(job_id)
            }
        )

# Create API router
api_router = APIRouter(prefix="/api")

@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    return [
        Project(id=p.id, name=p.name, description=p.description)
        for p in ProjectModel.list()
    ]

@api_router.post("/jobs/{project_id}", response_model=JobDetails)
async def create_job(project_id: str, background_tasks: BackgroundTasks):
    if not ProjectModel.find(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    
    job_id = JobModel.start(project_id)
    background_tasks.add_task(background_job, project_id, job_id)
    
    return JobDetails(
        project_id=project_id,
        job_id=job_id,
        status="started",
        total_tasks=0,
        task_status_map={},
        details={}
    )

@api_router.get("/jobs/{project_id}/{job_id}/status", response_model=JobDetails)
async def get_job_status(project_id: str, job_id: str):
    if not ProjectModel.find(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    
    job = JobModel.get_status(project_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    details = job.details or {}
    return JobDetails(
        project_id=project_id,
        job_id=job_id,
        status=job.status,
        total_tasks=job.total_tasks,
        current_task=job.current_task,
        task_status_map=details.get("status_map", {}),
        details=details
    )

@api_router.get("/runs/{project_id}", response_model=List[RecentRun])
async def get_recent_runs(
    project_id: str,
    limit: int = Query(5, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    if not ProjectModel.find(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    
    recent_jobs = JobModel.list_recent(project_id, limit, offset)
    
    runs = []
    for job in recent_jobs:
        job_data = job.details or {}
        # run = _generate_fake_run(job.id, job_data, job.created_at)
        # runs.append(run)
        model = job.get_model_summary()

        total = passed = failed = regression = score = 0
        task_status_map = job_data.get("status_map", {})
        if task_status_map:
            total = len(task_status_map)
            passed = sum(1 for status in task_status_map.values() if status == TaskStatus.COMPLETED)
            failed = sum(1 for status in task_status_map.values() if status == TaskStatus.FAILED)
            regression = total - passed - failed
            if total > 0:
                score = (passed / total)

        runs.append({
            "id": job.id,
            "created_at": job.created_at.replace(tzinfo=timezone.utc).isoformat(),
            "finished_at": job.finished_at.replace(tzinfo=timezone.utc).isoformat() if job.finished_at else None,
            # "status": job.status,
            "revision": job_data.get("revision", ""),
            "model": model,
            "score": score,
            "totalTests": total,
            "pass": passed,
            "fail": failed,
            "regression": regression,
            # "bookmarked": False,
            # "noted": False
        })
    
    return runs

def _get_task_details(task: TaskModel):
    return TaskDetails(
        id=task.id,
        job_id=task.job_id,
        challenge_id=task.challenge_id,
        status=task.status,
        error=task.error,
        task_input={'str': task.task_input} if type(task.task_input) == str else task.task_input,
        task_output={'str': task.task_output} if type(task.task_output) == str else task.task_output,
        task_details=task.task_details,
        task_logs={'logs': task.task_logs} if task.task_logs else None,
        eval_spec=task.eval_spec,
        eval_passed=task.eval_passed,
        eval_score=task.eval_score,
        eval_details=task.eval_details,
        eval_logs={'logs': task.eval_logs} if task.eval_logs else None,
        created_at=task.created_at.replace(tzinfo=timezone.utc).isoformat(),
        executed_at=task.executed_at.replace(tzinfo=timezone.utc).isoformat() if task.executed_at else None,
        evaluated_at=task.evaluated_at.replace(tzinfo=timezone.utc).isoformat() if task.evaluated_at else None,
        finished_at=task.finished_at.replace(tzinfo=timezone.utc).isoformat() if task.finished_at else None
    )

@api_router.get("/run-details/{run_id}", response_model=FullRunDetails)
async def get_run_details(run_id: str):
    job = JobModel.find(run_id)
    if not job:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Get project details
    project = ProjectModel.find(job.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all tasks for this job
    tasks = TaskModel.list(run_id)
    task_details = [_get_task_details(task) for task in tasks]
    
    # Create the full run details response
    return FullRunDetails(
        id=run_id,
        project=Project(
            id=project.id,
            name=project.name,
            description=project.description
        ),
        details=job.details or {},
        date=job.created_at.replace(tzinfo=timezone.utc).isoformat(),
        status=job.status,
        tasks=task_details
    )

# let's write a new API to find tasks with the same challenge ID
@api_router.get("/same-tasks/{project_id}/{challenge_id}", response_model=List[TaskDetails])
async def get_same_tasks(project_id: str, challenge_id: str, limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    tasks = TaskModel.find_same_tasks(project_id, challenge_id, limit, offset)
    return [_get_task_details(task) for task in tasks]
