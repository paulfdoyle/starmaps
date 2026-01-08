# Stage Action (reporestructure_phase01_stage_repo_structure_action.md)

- **Phase/Stage:** Phase 01 — Repo Structure (repo_structure).
- **Objective:** Define and build the new repository structure for the project.
- **Scope:** In: directory layout, naming conventions, top-level docs, migration entry points; Out: moving BCO1 code.
- **Acceptance:** Structure documented; directories created; DoD referenced.
- **Dependencies/data:** `AI_first/docs/process.md`, `AI_first/docs/projectplan.md`, `AI_first/projects/reporestructure/project_summary_reporestructure.md`
- **Outputs:** New structure created; updated docs describing the layout.
- **Definition of Done:** Persona notes filled, DoD checklist referenced, validation steps recorded.

## Personas (record outputs; use `AI_first/docs/templates/review_checklists.md`)
- Project Creator/Owner:
- Project/Process Manager:
  - Next actions: propose target repo layout + naming; inventory current top-level folders; draft archive approach for legacy code; list BCO1 entry point + dependencies for Phase 02.
  - Owners: Paul Doyle (structure proposal, approvals); Developer persona later to implement skeleton and migration notes.
  - Risks: hidden relative-path dependencies; dataset duplication; unclear BCO1 entry; large files inflating structure; breaking run docs.
  - Handoffs: finalize Phase 01 structure docs -> Developer builds directories; QA Lead validates doc links + run paths.
  - Target: complete Phase 01 structure proposal in the next working session.
- Developer:
- Developer:
  - Proposed structure (draft): `src/` (core Python), `scripts/` (CLI helpers), `data/` (datasets), `assets/` (images), `docs/` (project docs), `tests/`, `tools/` (one-off utilities), `archive/` (legacy code), plus top-level `README.md` + `pyproject.toml` (or `requirements.txt`).
  - Migration entry points: define a single runnable module (BCO1) under `src/` with a thin CLI wrapper in `scripts/`.
  - Data handling: standardize relative paths via a config/module (no hard-coded `../datasets`).
  - Inventory needed before Phase 02: exact BCO1 entry script, required datasets/images, any generated artifacts to exclude.
  - Risks: implicit imports from `python_scripts/`, path assumptions in scripts, and large binary assets.
- QA Lead:
- Optional personas (Product Manager, Repository Steward, Docs Expert, UI/Accessibility, Bug Triage, Automation/Tooling, Architect, Security, Ops/Observability, Performance/Cost, DBA):
- Optional personas (Product Manager, Repository Steward, Docs Expert, UI/Accessibility, Bug Triage, Automation/Tooling, Architect, Security, Ops/Observability, Performance/Cost, DBA):
  - Repository Steward:
    - Keep AI_first intact; new structure should live at repo root without mixing process assets.
    - Use `archive/` for legacy code (read-only) and document what's archived + why.
    - Align top-level layout with common Python repos (README, pyproject/requirements, src/tests/docs).
    - Avoid renaming existing AI_first paths; update run instructions instead.

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
- Pending.

## Documentation updates
- Pending.

## Issues & lessons
- Pending.
