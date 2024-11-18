from pydantic import BaseModel, Field
from typing import Optional, Dict


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
