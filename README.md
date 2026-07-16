# Wan2.2 Backend

FastAPI backend for Wan2.2 Studio.

## Run locally

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## Endpoints

- `GET /health`
- `POST /api/generate`
- `GET /api/status/{job_id}`
- `GET /api/download/{job_id}`
- `GET /api/gallery`
