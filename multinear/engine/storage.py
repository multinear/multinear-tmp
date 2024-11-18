from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.types import JSON
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import Dict, Any, Optional, List
import uuid


Base = declarative_base()

# Define SQLAlchemy models
class ProjectModel(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    folder = Column(String, nullable=False)
    jobs = relationship("JobModel", back_populates="project")

    @classmethod
    def list(cls) -> List["ProjectModel"]:
        with db_context() as db:
            return db.query(cls).all()

    @classmethod
    def find(cls, project_id: str) -> Optional["ProjectModel"]:
        with db_context() as db:
            return db.query(cls).filter(cls.id == project_id).first()

    @classmethod
    def save(cls, id: str, name: str, description: str, folder: str) -> "ProjectModel":
        with db_context() as db:
            project = db.query(cls).filter(cls.id == id).first()
            if project:
                project.name = name
                project.description = description
                project.folder = folder
            else:
                project = cls(id=id, name=name, description=description, folder=folder)
                db.add(project)
            db.commit()
            return project

    def to_dict(self):
        # remove SQLAlchemy internal state
        return {k:v for k,v in self.__dict__.items() if not k.startswith('_')}


class JobModel(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    status = Column(String, nullable=False)
    total_tasks = Column(Integer, default=0)
    current_task = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    project = relationship("ProjectModel", back_populates="jobs")
    tasks = relationship("TaskModel", back_populates="job")

    @classmethod
    def start(cls, project_id: str) -> str:
        """Start a new job and return its ID"""
        job_id = str(uuid.uuid4())
        with db_context() as db:
            job = cls(id=job_id, project_id=project_id, status="started")
            db.add(job)
            db.commit()
            return job_id

    @classmethod
    def find(cls, job_id: str) -> Optional["JobModel"]:
        with db_context() as db:
            return db.query(cls).filter(cls.id == job_id).first()

    def update(self, status: str, total_tasks: int = 0, current_task: Optional[int] = None, details: dict = None):
        with db_context() as db:
            job = db.query(JobModel).filter(JobModel.id == self.id).one()
            job.status = status
            job.total_tasks = total_tasks
            job.current_task = current_task
            if details is not None:
                job.details = details
            db.commit()
            # Update current instance
            self.status = status
            self.total_tasks = total_tasks
            self.current_task = current_task
            self.details = details

    @classmethod
    def list_recent(cls, project_id: str, limit: int = 5, offset: int = 0) -> List["JobModel"]:
        with db_context() as db:
            return (db.query(cls)
                   .filter(cls.project_id == project_id)
                   .order_by(cls.created_at.desc())
                   .offset(offset)
                   .limit(limit)
                   .all())

    @classmethod
    def get_status(cls, project_id: str, job_id: str) -> Optional["JobModel"]:
        """Get job status with project validation"""
        with db_context() as db:
            return (db.query(cls)
                   .filter(cls.id == job_id, cls.project_id == project_id)
                   .first())


class TaskStatus:
    STARTING = "starting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskModel(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    task_number = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    job = relationship("JobModel", back_populates="tasks")

    @classmethod
    def start(cls, job_id: str, task_number: int) -> str:
        """Start a new task and return its ID"""
        task_id = str(uuid.uuid4())
        with db_context() as db:
            task = cls(
                id=task_id,
                job_id=job_id,
                task_number=task_number,
                status=TaskStatus.RUNNING
            )
            db.add(task)
            db.commit()
            return task_id

    @classmethod
    def complete(cls, task_id: str, result: dict):
        """Mark task as completed with results"""
        with db_context() as db:
            task = db.query(cls).filter(cls.id == task_id).one()
            task.status = TaskStatus.COMPLETED
            task.result = result
            db.commit()

    @classmethod
    def fail(cls, task_id: str, error: str):
        """Mark task as failed with error"""
        with db_context() as db:
            task = db.query(cls).filter(cls.id == task_id).one()
            task.status = TaskStatus.FAILED
            task.error = error
            db.commit()

    @classmethod
    def list(cls, job_id: str):
        """List all tasks for a job"""
        with db_context() as db:
            return db.query(cls).filter(cls.job_id == job_id).all()

    @classmethod
    def get_status_map(cls, job_id: str) -> Dict[str, str]:
        """Get status map for all tasks in a job"""
        with db_context() as db:
            tasks = db.query(cls).filter(cls.job_id == job_id).all()
            return {task.id: task.status for task in tasks}


# Global variable to store SessionLocal
_SessionLocal = None

# Initialize SQLAlchemy
def init_db():
    DATABASE_URL = "sqlite:///./.multinear/multinear.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    global _SessionLocal
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

def _create_session():
    """Internal function to create a new database session."""
    global _SessionLocal
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()

@contextmanager
def db_context():
    """Get a database session as a context manager."""
    db = _create_session()
    try:
        yield db
    finally:
        db.close()

def get_db():
    """Get a database session - for FastAPI dependency injection."""
    with db_context() as db:
        yield db
