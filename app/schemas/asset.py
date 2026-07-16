from datetime import datetime

from pydantic import BaseModel


class AssetVersionResponse(BaseModel):
    id: str
    version_number: int
    storage_path: str
    created_at: datetime
    download_url: str


class AssetResponse(BaseModel):
    id: str
    project_id: str
    source_job_id: str | None = None
    asset_type: str
    title: str | None = None
    created_at: datetime
    latest_version: AssetVersionResponse | None = None
