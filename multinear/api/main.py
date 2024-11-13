from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from time import sleep
import uuid
from typing import Optional, Dict


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
job_status = {} # ephemeral

def background_job(job_id: str):
    """Simulate a long-running task"""
    job_status[job_id] = "running"
    # Simulate work
    for i in range(20):
        sleep(1)
        job_status[job_id] = f"running {i}"
    job_status[job_id] = "completed"

class JobResponse(BaseModel):
    job_id: str
    status: str
    details: Optional[Dict] = None

class JobStatusRequest(BaseModel):
    job_id: str

@app.post("/start", response_model=JobResponse)
async def start_job(background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    background_tasks.add_task(background_job, job_id)
    return JobResponse(
        job_id=job_id,
        status="started",
        # details={"message": "Job has been queued"}
    )

@app.post("/status", response_model=JobResponse)
async def get_job_status(request: JobStatusRequest):
    status = job_status.get(request.job_id, "not_found")
    details = {"progress": status} if status.startswith("running") else None
    return JobResponse(
        job_id=request.job_id,
        status=status,
        details=details
    )

app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")
