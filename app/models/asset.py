import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    source_job_id = Column(String, ForeignKey("ai_jobs.id"), nullable=True, index=True)
    asset_type = Column(String(32), nullable=False, default="video")
    title = Column(String(160), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
