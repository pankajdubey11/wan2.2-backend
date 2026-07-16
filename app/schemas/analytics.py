from pydantic import BaseModel


class AnalyticsOverviewResponse(BaseModel):
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    queued_jobs: int
    processing_jobs: int
    completion_rate: float
    avg_latency_seconds: float


class ModelUsageItem(BaseModel):
    model: str
    count: int
    completed: int
    failed: int
