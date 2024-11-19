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

class TaskDetails(BaseModel):
    id: str
    status: str
    result: Optional[Dict] = None
    error: Optional[str] = None

class FullRunDetails(BaseModel):
    id: str
    project: Project
    details: Dict
    date: str
    status: str
    tasks: List[TaskDetails]
