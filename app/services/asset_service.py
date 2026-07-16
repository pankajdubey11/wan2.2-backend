import hashlib
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.ai_job import AIJob
from app.models.asset import Asset
from app.models.asset_version import AssetVersion


def _sha256_of_file(file_path: str) -> str | None:
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return None

    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_asset_version_from_job(
    db: Session,
    *,
    job: AIJob,
    output_path: str,
    commit: bool = True,
) -> tuple[Asset, AssetVersion]:
    """
    Create immutable asset + v1 from completed AI job.
    """

    # One asset per job for MVP.
    asset = Asset(
        project_id=job.project_id,
        source_job_id=job.id,
        asset_type="video",
        title=(job.prompt[:120] if job.prompt else "Generated Video"),
        description=None,
    )
    db.add(asset)
    db.flush()

    checksum = _sha256_of_file(output_path)
    metadata = {
        "model": job.model,
        "size": job.size,
        "steps": job.steps,
        "guidance_scale": job.guidance_scale,
        "seed": job.seed,
        "source_job_id": job.id,
    }

    version = AssetVersion(
        asset_id=asset.id,
        version_number=1,
        storage_path=output_path,
        checksum=checksum,
        metadata_json=json.dumps(metadata),
    )
    db.add(version)

    if commit:
        db.commit()
        db.refresh(asset)
        db.refresh(version)

    return asset, version
