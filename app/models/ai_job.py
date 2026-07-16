import datetime
import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.database import Base


class AIJob(Base):
    __tablename__ = "ai_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    workflow_execution_id = Column(
        String,
        ForeignKey("workflow_executions.id"),
        nullable=False,
        index=True,
    )

    status = Column(String(32), nullable=False, default="queued")
    progress = Column(Float, nullable=False, default=0.0)

    model = Column(String(64), nullable=False, default="ti2v-5b")
    prompt = Column(Text, nullable=False)
    image_path = Column(String, nullable=True)
    steps = Column(Integer, nullable=False, default=30)
    guidance_scale = Column(Float, nullable=False, default=6.0)
    seed = Column(Integer, nullable=True)
    size = Column(String(32), nullable=False, default="704*1280")

    output_path = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
