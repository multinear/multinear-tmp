from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.types import JSON
from datetime import datetime, timezone
from contextlib import contextmanager


Base = declarative_base()

# Define SQLAlchemy models
class ProjectModel(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    folder = Column(String, nullable=False)
    jobs = relationship("JobModel", back_populates="project")

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
    def start(cls, task_id: str, job_id: str, task_number: int):
        """Start a new task"""
        with db_context() as db:
            task = cls(
                id=task_id,
                job_id=job_id,
                task_number=task_number,
                status="running"
            )
            db.add(task)
            db.commit()
            return task

    def complete(self, result: dict):
        """Mark task as completed with results"""
        with db_context() as db:
            db_task = db.query(TaskModel).filter(TaskModel.id == self.id).one()
            db_task.status = "completed"
            db_task.result = result
            db.commit()
            # Update current instance
            self.status = "completed"
            self.result = result

    def fail(self, error: str):
        """Mark task as failed with error"""
        with db_context() as db:
            db_task = db.query(TaskModel).filter(TaskModel.id == self.id).one()
            db_task.status = "failed"
            db_task.error = error
            db.commit()
            # Update current instance
            self.status = "failed"
            self.error = error

    @classmethod
    def list(cls, job_id: str):
        """List all tasks for a job"""
        with db_context() as db:
            return db.query(cls).filter(cls.job_id == job_id).all()


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
