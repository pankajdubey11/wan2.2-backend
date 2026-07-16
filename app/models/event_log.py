import datetime
import uuid

from sqlalchemy import Column, DateTime, JSON, String

from app.database import Base


class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(64), nullable=False, index=True)
    domain = Column(String(64), nullable=False, index=True)
    entity_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=True, index=True)
    job_id = Column(String, nullable=True, index=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
