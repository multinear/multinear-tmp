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
