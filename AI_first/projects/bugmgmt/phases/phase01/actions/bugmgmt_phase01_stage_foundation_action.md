# Stage Action (bugmgmt_phase01_stage_foundation_action.md)

- **Phase/Stage:** Phase 01 — Foundation.
- **Objective:** Define BugMgmt workflows, issue fields, and UI expectations.
- **Scope:** In: schema and workflow docs, UI behavior notes; Out: integrations.
- **Acceptance:** Persona notes recorded; schema/workflow expectations documented; DoD referenced.
- **Dependencies/data:** `AI_first/bugmgmt/issues/issues.jsonl`, `AI_first/scripts/issues.py`, `AI_first/ui/bugmgmt_issues.html`.
- **Outputs:** Updated phase/stage docs and any related process updates.
- **Definition of Done:** Persona notes filled, DoD checklist referenced, validation steps recorded.

## Personas (record outputs; use `AI_first/docs/templates/review_checklists.md`)
- Project/Process Manager: Workflow is JSONL → export JSON/HTML → review UI; keep fields minimal and consistent; focus on a single local source of truth; deterministic exports; PII-free data; document rules in process docs; regenerate HTML report after every bug change.
- Developer: Details column should show Summary by default; show optional fields only when present; fallback opened date to `date`.
- QA Lead: Validate new bugs render, filters work, Details shows expected fields, closed bugs show closure note/date, and sort order is stable.
- Docs Expert: Keep `AI_first/docs/process.md`, `AI_first/docs/projectplan.md`, `README.md`, and `AGENTS.md` aligned with the BugMgmt workflow.
- Optional personas (Product Manager, Repository Steward, UI/Accessibility, Bug Triage, Automation/Tooling, Architect, Security, Ops/Observability, Performance/Cost, DBA): Not triggered; keep offline/local only and avoid schema drift.

## Plan
- Review current BugMgmt schema and UI behavior.
- Confirm required fields and export flow.
- Define UI/table expectations (sorting, Details column, filters).

## Execution notes
- Created `bugmgmt` project docs and removed the sample project.
- Updated issue data to use the `bugmgmt` project and regenerated exports.
- Adjusted Details column rendering to show Summary and avoid empty lines.

## Validation
- Regenerate exports and verify UI renders correctly.
- Confirm Details shows Summary for each issue and no empty sections appear.

## Documentation updates
- Updated `AI_first/docs/projectplan.md`, `AI_first/docs/process.md`, `README.md`, and `AGENTS.md`.

## Close-out
- Phase 01 objectives met; workflow and UI behavior documented.
- Issue detail view implemented and validated; no open bugs remain.
- Closed on 2025-12-22.

## Issues & lessons
- Standard detail fields for BugMgmt entries: `root_cause`, `proposed_fix`, `qa_reproduction`.
