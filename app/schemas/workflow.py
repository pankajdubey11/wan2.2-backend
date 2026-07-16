from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GenerateWorkflowRequest(BaseModel):
    project_id: str = Field(..., description="Project identifier")
    model: str = Field(default="ti2v-5b")
    prompt: str = Field(..., min_length=1)
    image: Optional[str] = Field(default=None, description="Base64 image or URL/path")
    steps: int = Field(default=30, ge=1, le=120)
    guidance_scale: float = Field(default=6.0, ge=0.0, le=30.0)
    seed: Optional[int] = None
    size: str = Field(default="704*1280")


class GenerateWorkflowResponse(BaseModel):
    workflow_execution_id: str
    job_id: str
    status: str
    estimated_seconds: int = 540


class AIJobStatusResponse(BaseModel):
    job_id: str
    project_id: str
    workflow_execution_id: str
    status: str
    progress: float
    output_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
