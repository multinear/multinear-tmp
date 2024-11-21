from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class Project(BaseModel):
    id: str
    name: str
    description: str

class JobDetails(BaseModel):
    project_id: str
    job_id: str
    status: str
    total_tasks: int
    current_task: Optional[int] = None
    task_status_map: Optional[Dict] = None
    details: Optional[Dict] = None

class RecentRun(BaseModel):
    id: str
    revision: str
    model: str
    score: float
    totalTests: int
    pass_: int = Field(alias='pass')  # 'pass' is a Python keyword
    fail: int
    regression: int
    bookmarked: Optional[bool] = False
    noted: Optional[bool] = False
    created_at: str
    finished_at: Optional[str] = None

class TaskDetails(BaseModel):
    id: str
    challenge_id: str
    job_id: str
    status: str
    error: Optional[str] = None
    task_input: Optional[Dict] = None
    task_output: Optional[Dict] = None
    task_details: Optional[Dict] = None
    task_logs: Optional[Dict] = None
    eval_spec: Optional[Dict] = None
    eval_passed: Optional[bool] = None
    eval_score: Optional[float] = None
    eval_details: Optional[Dict] = None
    eval_logs: Optional[Dict] = None
    created_at: str
    executed_at: Optional[str] = None
    evaluated_at: Optional[str] = None
    finished_at: Optional[str] = None

class FullRunDetails(BaseModel):
    id: str
    project: Project
    details: Dict
    date: str
    status: str
    tasks: List[TaskDetails]
