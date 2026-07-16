# Wan2.2 Backend

FastAPI backend for Wan2.2 Studio.

## Run locally

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## Endpoints

- `GET /health`
- Legacy MVP endpoints:
  - `POST /api/generate`
  - `GET /api/status/{job_id}`
  - `GET /api/download/{job_id}`
  - `GET /api/gallery`
- Sprint 1 SDPS-aligned endpoints:
  - `GET /api/projects`
  - `POST /api/projects`
  - `POST /api/workflows/generate`
  - `GET /api/ai-jobs/{job_id}`
  - `GET /api/ai-jobs/{job_id}/download`

## Sprint 1 Notes

- `project_id` is required for workflow submission.
- A default project is auto-seeded on startup for local development.
- AI lifecycle events are persisted in `event_logs`.
