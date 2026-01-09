# Stage Action (reporestructure_phase01_stage_repo_structure_action.md)

- **Phase/Stage:** Phase 01 — Repo Structure (repo_structure).
- **Objective:** Define and build the new repository structure for the project.
- **Scope:** In: directory layout, naming conventions, top-level docs, migration entry points; Out: moving BCO1 code.
- **Acceptance:** Structure documented; directories created; DoD referenced.
- **Dependencies/data:** `AI_first/docs/process.md`, `AI_first/docs/projectplan.md`, `AI_first/projects/reporestructure/project_summary_reporestructure.md`
- **Outputs:** New structure created; updated docs describing the layout.
- **Definition of Done:** Persona notes filled, DoD checklist referenced, validation steps recorded.
- **Status:** Closed (Phase 01 complete; outstanding data-duplication decision tracked separately).

## Personas (record outputs; use `AI_first/docs/templates/review_checklists.md`)
- Project Creator/Owner:
  - Approved target layout and archive-only constraint; confirmed BCO1 as Phase 02 entry point.
- Project/Process Manager:
  - Status: structure defined and skeleton created; Phase 01 scope met pending validation/doc cleanup.
  - Next actions: resolve dataset-duplication plan (RPR-2026-01-003); update project summary to Phase 02; handoff to QA for structure verification.
  - Risks: hidden relative-path dependencies; dataset duplication; large legacy artifacts.
  - Handoffs: QA validates directory layout + docs; Developer applies archive-only changes.
- Developer:
  - Implemented skeleton layout (`src/`, `scripts/`, `data/`, `assets/`, `docs/`, `tests/`, `tools/`, `archive/`) with `.gitkeep` placeholders.
  - Defined repo-root path conventions to avoid `../datasets` assumptions.
- QA Lead:
  - Validate directories exist, AI_first remains untouched, and docs reference the new layout.
  - Confirm no deletions; legacy content only archived.
- Optional personas:
  - Repository Steward: preserve AI_first; archive legacy; keep canonical data under `data/`.
- DoD checklist reference: `AI_first/docs/templates/review_checklists.md`

## Plan
- Confirm target repo structure and naming conventions.
- Document migration entry points and archive approach.
- Record acceptance and validation steps.
- Proposed repo tree (draft):
  ```
  .
  ├── src/
  │   └── starmaps/
  ├── scripts/
  │   └── run_bco1.py
  ├── data/
  │   ├── raw/
  │   └── processed/
  ├── assets/
  │   └── images/
  ├── docs/
  ├── tests/
  ├── tools/
  ├── archive/
  │   └── legacy_python_scripts/
  ├── AI_first/
  ├── README.md
  └── pyproject.toml (or requirements.txt)
  ```
- Skeleton creation plan (Phase 01):
  - Create empty directories now: `src/`, `scripts/`, `data/`, `assets/`, `docs/`, `tests/`, `tools/`, `archive/`.
  - Add placeholder files where needed to preserve empty dirs (e.g., `.gitkeep`).
  - Leave existing code/data in place until Phase 02 migration.

## Execution notes
- Skeleton created (Phase 01):
  - Directories: `src/`, `src/starmaps/`, `scripts/`, `data/raw/`, `data/processed/`, `assets/images/`, `docs/`, `tests/`, `tools/`, `archive/legacy_python_scripts/`.
  - `.gitkeep` placeholders added to preserve empty directories.
- Canonical entry point (Phase 02 target):
  - BCO1: `src/starmaps/bco1.py` (migrated from `python_scripts/BCO-Demo1.py`).
  - Legacy: `archive/legacy_python_scripts/BCO-Demo2.py` (archived).
- Inventory (BCO1 candidate):
  - Entry point: `src/starmaps/bco1.py` (has `main()` and `if __name__ == "__main__": main()`).
  - Alternate demo: `python_scripts/BCO-Demo2.py` (needs verification, but not the initial target).
  - Dataset dependency: `datasets/updated_merged_star_exo_data.json` (primary); `datasets/star_database_colors.json` appears as legacy/commented option.
  - Output directory: `saved_images/` (relative to run CWD).
  - Python deps: `pygame`, `pandas`, `numpy`, `skyfield`, `pyquaternion`, `numba`, `astroquery` (Simbad imported), plus standard libs.
  - OS-specific deps: `AppKit` on macOS, `ctypes` on Windows.
  - Known path risk: hard-coded `../datasets/` relative to `python_scripts/`.

## Validation
- Confirmed skeleton directories and placeholder files exist.
- Reviewed structure/run notes in repository docs.
- Runtime validation deferred to Phase 02 (BCO1 execution).

## Documentation updates
- Added contributor guide `AGENTS.md` for the new layout.
- Documented repository structure and entry point in `README.md`.

## Issues & lessons
- Dataset duplication remains open pending archive plan (RPR-2026-01-003).
- Archive-only rule reduces risk; avoid destructive cleanup without approval.
