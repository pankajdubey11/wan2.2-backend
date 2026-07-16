from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.asset import Asset
from app.models.asset_version import AssetVersion
from app.schemas.asset import AssetResponse, AssetVersionResponse

router = APIRouter(tags=["assets"])


@router.get("/api/projects/{project_id}/assets", response_model=list[AssetResponse])
async def list_project_assets(project_id: str, db: Session = Depends(get_db)):
    assets = (
        db.query(Asset)
        .filter(Asset.project_id == project_id)
        .order_by(Asset.created_at.desc())
        .all()
    )

    result: list[AssetResponse] = []
    for asset in assets:
        latest = (
            db.query(AssetVersion)
            .filter(AssetVersion.asset_id == asset.id)
            .order_by(AssetVersion.version_number.desc())
            .first()
        )
        latest_resp = None
        if latest:
            latest_resp = AssetVersionResponse(
                id=latest.id,
                version_number=latest.version_number,
                storage_path=latest.storage_path,
                created_at=latest.created_at,
                download_url=f"/api/assets/{asset.id}/versions/{latest.id}/download",
            )

        result.append(
            AssetResponse(
                id=asset.id,
                project_id=asset.project_id,
                source_job_id=asset.source_job_id,
                asset_type=asset.asset_type,
                title=asset.title,
                created_at=asset.created_at,
                latest_version=latest_resp,
            )
        )

    return result


@router.get("/api/assets/{asset_id}/versions/{version_id}/download")
async def download_asset_version(asset_id: str, version_id: str, db: Session = Depends(get_db)):
    version = (
        db.query(AssetVersion)
        .filter(AssetVersion.id == version_id, AssetVersion.asset_id == asset_id)
        .first()
    )
    if not version:
        raise HTTPException(status_code=404, detail="Asset version not found")

    if not Path(version.storage_path).exists():
        raise HTTPException(status_code=404, detail="Asset file not found")

    filename = f"{asset_id}_v{version.version_number}.mp4"
    return FileResponse(version.storage_path, media_type="video/mp4", filename=filename)
