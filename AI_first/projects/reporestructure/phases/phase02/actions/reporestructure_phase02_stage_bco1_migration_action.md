# Stage Action (reporestructure_phase02_stage_bco1_migration_action.md)

- **Phase/Stage:** Phase 02 — BCO1 Migration & Archive (bco1_migration).
- **Objective:** Move the initial BCO1 Python program and required support into the new structure; archive legacy content.
- **Scope:** In: identify BCO1 entry point, dependencies, datasets/assets; migrate and document; Out: refactors or performance tuning.
- **Acceptance:** BCO1 runs from new structure; legacy code archived; DoD referenced.
- **Dependencies/data:** `AI_first/projects/reporestructure/phases/phase01/`, `AI_first/docs/process.md`.
- **Outputs:** Migrated BCO1 code path, archive location, updated run notes.
- **Definition of Done:** Persona notes filled, DoD checklist referenced, validation steps recorded.
- **Status:** Closed (Phase 02 complete; Phase 03 performance review next).

## Personas (record outputs; use `AI_first/docs/templates/review_checklists.md`)
- Project/Process Manager:
  - Status: BCO1 migrated to `src/` with runner, dataset moved to `data/processed/`, output dir standardized, legacy demo archived.
  - Next actions: run validation pass; resolve dataset-duplication plan (RPR-2026-01-003); prepare Phase 03 performance review notes.
  - Risks: dataset duplication; OS-specific deps; migration scope expanded by stability fixes.
  - Handoffs: QA validates runtime behavior; Developer keeps archive-only changes.
- Developer:
  - Implemented repo-root path config, runner script, standardized output directory, and exit behavior fixes.
  - Deviations: applied UI/performance stability fixes to keep BCO1 usable; tracked in BugMgmt.
- QA Lead:
  - Validate `python3 scripts/run_bco1.py` loads data and exits cleanly.
  - Confirm menu selection, slider/arrow controls, and star selection highlight.
- Optional personas:
  - Repository Steward: preserve AI_first; archive legacy artifacts only; keep canonical data under `data/`.
- DoD checklist reference: `AI_first/docs/templates/review_checklists.md`

## Plan
- Inventory required files and dependencies for BCO1.
- Move code/data into new structure and document paths.
- Archive remaining code and record rationale.

## Execution notes
- Migration executed:
  - Moved `python_scripts/BCO-Demo1.py` -> `src/starmaps/bco1.py`.
  - Added runner `scripts/run_bco1.py` (imports `starmaps.bco1`).
  - Moved dataset `datasets/updated_merged_star_exo_data.json` -> `data/processed/updated_merged_star_exo_data.json`.
  - Updated BCO1 dataset paths to use `data/processed/` and repo-root resolution.
  - Archived legacy demo: `python_scripts/BCO-Demo2.py` -> `archive/legacy_python_scripts/BCO-Demo2.py`.
  - Standardized output location: `assets/images/generated/` (directory created).
  - Fixed import-time `pygame.quit()` causing font module errors; cleanup now happens at end of `main()`.
  - Documented canonical run command in `README.md` (`python3 scripts/run_bco1.py`).
- Inventory (BCO1 migration targets):
  - `scripts/`:
    - `python_scripts/BCO-Demo1.py` -> `scripts/run_bco1.py` (thin CLI wrapper).
  - `src/`:
    - `python_scripts/BCO-Demo1.py` -> `src/starmaps/bco1.py` (core module with `main()`).
  - `data/processed/`:
    - `datasets/updated_merged_star_exo_data.json` (primary dataset).
    - `datasets/star_database_colors.json` (legacy fallback; optional).
  - `assets/images/`:
    - `saved_images/` output directory (rename/move; consider `assets/images/generated/`).
  - `archive/legacy_python_scripts/`:
    - `python_scripts/BCO-Demo2.py` (archive; not migrated).

## Validation
- Completed: ran `python3 scripts/run_bco1.py` after latest fixes.
- Confirmed dataset loads from `data/processed/` and output writes to `assets/images/generated/`.
- Exit button and ESC quit terminate cleanly.

## Documentation updates
- `README.md` updated with canonical run command and new paths.
- `AGENTS.md` created to document contributor guidelines for the new structure.

## Issues & lessons
- Dataset duplication risk remains open pending archive plan (RPR-2026-01-003).
- Archive-only rule reduces migration risk; avoid deleting legacy artifacts without approval.
