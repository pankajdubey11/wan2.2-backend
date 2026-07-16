# PRD Alignment Plan (SDPS-002)

- Document: PRD Alignment for Wan2.2 Studio
- Input Reference: SDPS-002 Product Architecture & Domain Model (v2.0 Draft)
- Date: 2026-07-16
- Status: Draft for sign-off

## 1) Review Summary

Your SDPS-002 architecture is strong and production-grade. The most important principles to preserve are:

1. **Domain separation** (single owner per business capability)
2. **AI Gateway abstraction** (UI never calls model runtime directly)
3. **Workflow-first orchestration** (user action -> workflow -> gateway -> infra)
4. **Open-source AI model policy**
5. **Event-driven lifecycle**

This is compatible with our current direction, but our current codebase is an MVP scaffold and needs explicit domain boundaries and traceability IDs.

## 2) Gap Analysis vs Current Implementation

### What is already aligned

- Frontend -> Backend API pattern (no direct model access from UI)
- Async job lifecycle exists (`queued/processing/completed/failed`)
- Output persistence + gallery endpoint exists
- Local mock mode enables workflow testing without GPU

### Gaps to close

- No explicit **domain ownership map** in code
- No **AI Gateway module** separate from worker runtime concerns
- No **workflow orchestration layer** (currently direct generation request)
- No standardized **event contracts**
- No **traceability IDs** (Domain/Module/Feature/FR)
- Billing/credits validation not in request path
- Analytics/audit events not persisted

## 3) Domain Scope for MVP (SDPS-aligned)

To keep MVP achievable while staying aligned, we implement a subset of domains first.

### P0 Domains (must ship in MVP)

- **D03 Projects** (minimal project context per generation)
- **D04 Asset Library** (asset persistence + immutable output versions)
- **D06 Creative Workflow** (workflow definitions and execution records)
- **D07 AI Gateway** (validation, routing, queueing, status)
- **D08 AI Infrastructure** (worker execution, model registry basics)

### P1 Domains (early post-MVP)

- **D01 Identity & Access** (auth + session)
- **D10 Notifications** (job completion/failure)
- **D11 Analytics** (usage, latency, model success rate)

### P2 Domains

- **D02 Workspace**
- **D05 Prompt Intelligence**
- **D09 Billing** (credits, wallet, subscription)
- **D12 Administration** (feature flags, moderation, queue ops)

## 4) Service Ownership Plan (MVP)

We adopt a **modular monolith first**, with explicit module boundaries matching SDPS service ownership. Later we can split into microservices without breaking contracts.

### Backend Module Ownership (inside current backend repo)

- `identity` (placeholder in MVP)
- `projects`
- `assets`
- `workflow`
- `ai_gateway`
- `ai_worker_adapter`
- `notifications` (placeholder)
- `analytics` (placeholder)
- `admin` (placeholder)

### Critical rule

- Frontend may call only API routes.
- API routes must call `workflow` / `ai_gateway` modules.
- `ai_gateway` is the only module allowed to submit to worker queue.

## 5) Required Event Contracts (MVP)

Adopt canonical events from SDPS-002:

1. `project.created`
2. `asset.uploaded`
3. `ai_job.submitted`
4. `ai_job.started`
5. `ai_job.completed`
6. `asset.created`
7. `project.updated`
8. `notification.sent` (P1)
9. `analytics.recorded` (P1)

Event payload minimum:

- `event_id`
- `event_type`
- `timestamp`
- `domain`
- `entity_id`
- `job_id` (if AI-related)
- `actor_id` (when identity is enabled)

## 6) Data Ownership Rules (Implementation)

Enforce these now so refactor cost stays low:

1. `projects` owns project metadata
2. `assets` owns asset rows + asset versions (immutable)
3. `workflow` owns execution rows
4. `ai_gateway` owns AI job rows + state transitions
5. other modules reference by ID only

## 7) Traceability Convention (Mandatory)

Adopt SDPS format in tickets, docs, and code comments:

- Domain: `D07`
- Module: `AIGW-JOB`
- Feature: `AIGW-JOB-SUBMIT`
- Requirement: `AIGW-JOB-FR-001`

Example set:

- `AIGW-JOB-FR-001`: Validate generation request before enqueue
- `AIGW-JOB-FR-002`: Create AI job in `queued` state
- `AIGW-JOB-FR-003`: Emit `ai_job.submitted`
- `AIGW-JOB-FR-004`: Return `job_id` within 1 second

## 8) PRD-Driven Build Plan

## Phase 0: Architecture Refactor (1 sprint)

Deliverables:

- Restructure backend by SDPS modules
- Define event schema + event logger
- Introduce requirement IDs in API spec

Exit criteria:

- All generation routes call `workflow -> ai_gateway`
- No direct route-to-worker execution path

## Phase 1: MVP Core (2 sprints)

Deliverables:

- Project context in generation requests
- Immutable asset version records for outputs
- Workflow execution table
- AI Gateway state machine + retry policy (basic)

Exit criteria:

- Full event chain from submit to asset creation
- Gallery sourced from `assets`, not ad-hoc output scan

## Phase 2: Product Hardening (1 sprint)

Deliverables:

- Basic identity
- Notification hooks (in-app)
- Analytics counters and latency dashboards

Exit criteria:

- User-scoped history
- Job completion notifications
- Basic usage reporting

## 9) API/Frontend Impact

Frontend changes required after refactor:

1. Include `project_id` in generation request
2. Poll status through AI Gateway endpoints only
3. Gallery uses asset API contract (`asset_id`, `version_id`, `source_job_id`)

Backend endpoint shape (target):

- `POST /api/workflows/generate`
- `GET /api/ai-jobs/{job_id}`
- `GET /api/assets?project_id=...`
- `GET /api/assets/{asset_id}/versions/{version_id}/download`

## 10) Decisions Needed to Finalize PRD v1.0

Please confirm these 6 items:

1. **Architecture path**: modular monolith first -> microservices later (recommended)
2. **MVP project model**: require `project_id` for every generation request
3. **Event bus for MVP**: start with DB-backed event log (recommended) vs external broker now
4. **Billing in MVP**: deferred (Phase 2) or minimal credit check in MVP
5. **Identity in MVP**: deferred (single-tenant alpha) or include basic login now
6. **Default model policy**: `ti2v-5b` default with preset profiles

## 11) Recommended Immediate Next Step

After approval, we produce:

- `SDPS-003` style module catalog for this codebase
- Endpoint contract v1 with requirement IDs
- Sprint backlog mapped to Domain/Module/Feature/FR
