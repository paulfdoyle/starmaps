# Stage Action (project_management_phase03_stage_consolidation_under_single_directory_action.md)

- **Phase/Stage:** Phase 03 — Consolidation under single directory.
- **Objective:** Consolidate process, BugMgmt, and project management assets under `AI_first/` and update references.
- **Scope:** In: inventory PM docs/UI assets, move planning docs to `AI_first/projects/`, remove empty workspace directories, path/link updates, doc rendering checks. Out: content redesign or automation.
- **Acceptance:** Assets live under `AI_first/`; empty workspace directories removed; references updated in project/phase docs and `AI_first/ui/PM.html`; docs render without broken links.
- **Dependencies/data:** `AI_first/docs/projectplan.md`, `AI_first/projects/project_management/`, `AI_first/ui/PM.html`, `AI_first/ui/project_project_management.html`, `AI_first/ui/docs/`.
- **Outputs:** Asset inventory, consolidation plan, updated paths, validation notes.
- **Definition of Done:** Acceptance met; persona notes filled; validation captured.

## Personas (record outputs; use `AI_first/docs/templates/review_checklists.md`)
- Project/Process Manager: Confirmed the drop-in goal: keep all process/BugMgmt/PM artifacts under `AI_first/`, remove empty workspace dirs, and update docs/scripts to point at `AI_first/projects/`.
- Developer: Consolidated project planning docs and references under `AI_first/`; updated render scripts and refreshed PM/project detail views.
- QA Lead: Spot-checked PM.html and project detail pages for link resolution and rendering consistency.
- Optional personas (Product Manager, Repository Steward, Docs Expert, UI/Accessibility, Bug Triage, Automation/Tooling, Architect, Security, Ops/Observability, Performance/Cost, DBA):
- Docs Expert: Updated process and persona docs plus the process guide to align with the consolidated layout.
- Automation/Tooling: Ran the doc and PM render scripts to keep UI outputs in sync.

## Plan
- Inventory PM-related files and current references.
- Set `AI_first/` as the target root and `AI_first/projects/` as the planning docs root.
- Move files, remove empty workspace directories, and update links/paths.
- Regenerate docs and validate links.

## Execution notes
- Verified process, BugMgmt, and project management assets live under `AI_first/`.
- Updated docs/templates to align prompts, persona ordering, and consolidated paths.
- Regenerated PM and docs UI outputs from the updated sources.

## Validation
- Ran `python3 AI_first/scripts/render_docs.py` and `python3 AI_first/scripts/render_pm.py`.
- Spot-checked `AI_first/ui/PM.html` and `AI_first/ui/project_project_management.html` for resolved links.
- Confirmed `AI_first/ui/docs/` renders the updated markdown outputs.

## Documentation updates
- Updated `AI_first/docs/projectplan.md` and project summary to reflect Phase 03 completion.
- Updated phase docs and stage action with completion status and close-out notes.
- Refreshed the process guide and persona docs after consolidation updates.

## Issues & lessons
- None noted.
