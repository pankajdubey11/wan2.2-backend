import datetime
import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, JSON, String, Text

from app.database import Base


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    workflow_type = Column(String(64), nullable=False, default="generate_video")
    status = Column(String(32), nullable=False, default="queued")
    progress = Column(Float, nullable=False, default=0.0)
    input_payload = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
