# PRD: Wan2.2 Studio Platform (v1.0)

- Status: Final (Approved)
- Date: 2026-07-16
- Architecture Baseline: SDPS-002

## 1. Product Intent

Wan2.2 Studio is a workflow-first AI creative platform for video generation using open-source models. Users generate videos from text and image prompts through a web interface, while backend services orchestrate jobs via an AI Gateway and worker infrastructure.

## 2. Confirmed Product Decisions

1. Architecture: **Modular monolith first**, microservice split later.
2. Project model: **`project_id` required** for all generation requests.
3. Eventing: **DB-backed event log** in MVP.
4. Billing: **Deferred to Phase 2**.
5. Identity: **Deferred for single-tenant alpha**.
6. Default model: **`ti2v-5b`** with quality/speed presets.

## 3. MVP Goals

- Deliver T2V + I2V generation via workflow-driven APIs.
- Enforce domain ownership and service boundaries.
- Persist jobs/assets/workflow state with traceable events.
- Support local development without GPU using mock mode.

## 4. Domain Scope (SDPS-Aligned)

### P0 (MVP)

- D03 Projects
- D04 Asset Library
- D06 Creative Workflow
- D07 AI Gateway
- D08 AI Infrastructure

### P1

- D10 Notifications
- D11 Analytics

### P2

- D01 Identity & Access
- D09 Billing
- D12 Administration enhancements

## 5. Functional Requirements

- FR-001: Create workflow execution for generation request.
- FR-002: Validate request in AI Gateway before enqueue.
- FR-003: Persist AI job with state transitions (`queued`, `processing`, `completed`, `failed`).
- FR-004: Emit lifecycle events for every transition.
- FR-005: Create immutable asset version on successful completion.
- FR-006: Expose downloadable MP4 via asset version endpoint.
- FR-007: Require `project_id` in generation API.
- FR-008: Provide status polling endpoint with progress.
- FR-009: Provide project-scoped gallery endpoint.
- FR-010: Support local mock generation path.

## 6. Non-Functional Requirements

- NFR-001: Job submission API p95 < 1s (excluding upload transfer).
- NFR-002: Health endpoint p95 < 300ms.
- NFR-003: Structured error payloads for all failures.
- NFR-004: All job logs include `job_id`.
- NFR-005: No direct frontend-to-model communication.

## 7. Data Ownership

- Projects module owns project entities.
- Assets module owns assets and immutable versions.
- Workflow module owns workflow definitions/executions.
- AI Gateway owns AI jobs and status transitions.
- Modules reference foreign entities by ID only.

## 8. Event Contracts (MVP)

- `ai_job.submitted`
- `ai_job.started`
- `ai_job.completed`
- `ai_job.failed`
- `asset.created`
- `project.updated`

Each event includes:

- `event_id`, `event_type`, `timestamp`, `domain`, `entity_id`, `job_id`, `project_id`

## 9. API Surface (MVP v1)

- `POST /api/workflows/generate`
- `GET /api/ai-jobs/{job_id}`
- `GET /api/projects/{project_id}/assets`
- `GET /api/assets/{asset_id}/versions/{version_id}/download`
- `GET /health`

## 10. Success Criteria

MVP is successful when:

1. User can generate T2V and I2V with valid `project_id`.
2. Status and progress are visible until completion.
3. Completed jobs always create asset versions.
4. Project gallery lists generated outputs reliably after restart.
5. Local mock mode enables full E2E dev/testing without GPU.
