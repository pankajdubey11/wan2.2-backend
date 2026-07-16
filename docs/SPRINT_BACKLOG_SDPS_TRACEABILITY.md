# Sprint Backlog (SDPS Traceability)

- Status: Ready for execution
- Basis: PRD v1.0 + SDPS-002

## Sprint 1: Architecture Refactor (P0 Foundation)

### D06 Workflow

- WF-DEF-FR-001: Add workflow execution entity and repository.
- WF-API-FR-002: Implement `POST /api/workflows/generate`.
- WF-API-FR-003: Enforce `project_id` requirement.

### D07 AI Gateway

- AIGW-JOB-FR-001: Request validation module.
- AIGW-JOB-FR-002: AI job state machine (`queued/processing/completed/failed`).
- AIGW-JOB-FR-003: Implement `GET /api/ai-jobs/{job_id}`.
- AIGW-EVT-FR-004: Persist lifecycle events in event log table.

### D08 AI Infrastructure

- AIINF-WRK-FR-001: Worker adapter interface (`mock`, `wan22`).
- AIINF-WRK-FR-002: Progress callback standardization.

## Sprint 2: Asset + Project Integrity

### D03 Projects

- PRJ-ENT-FR-001: Minimal project entity and lookup API.
- PRJ-REL-FR-002: Link workflows/jobs/assets to `project_id`.

### D04 Asset Library

- AST-ENT-FR-001: Asset entity + immutable asset version entity.
- AST-API-FR-002: Implement `GET /api/projects/{project_id}/assets`.
- AST-API-FR-003: Implement versioned download endpoint.
- AST-RULE-FR-004: Enforce immutable version creation on job completion.

### D07 AI Gateway

- AIGW-COMP-FR-005: On completion, create asset + version atomically.
- AIGW-FAIL-FR-006: Persist failure reason with retry metadata.

## Sprint 3: Product Hardening

### D10 Notifications (P1)

- NOTIF-EVT-FR-001: Emit notification-ready events on completion/failure.

### D11 Analytics (P1)

- ANL-JOB-FR-001: Track submission count, completion rate, avg latency.
- ANL-MDL-FR-002: Track model usage by preset and project.

### Cross-cutting

- OPS-LOG-NFR-001: Structured logging with `job_id` and `project_id`.
- OPS-ERR-NFR-002: Standardized API error envelope.
- OPS-DOC-NFR-003: OpenAPI examples for all MVP endpoints.

## Definition of Done (Per Story)

- Requirement ID mapped in PR title/description.
- Unit tests for validation/state transitions.
- API contract updated in docs.
- Event emitted and persisted where applicable.
- Reviewed against domain ownership rules.
