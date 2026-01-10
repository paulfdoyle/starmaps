# Stage Action (reporestructure_phase03_stage_performance_review_action.md)

- **Phase/Stage:** Phase 03 — Performance & Technical Review (performance_review).
- **Status:** Complete (2026-01-09).
- **Objective:** Review performance and technical structure; document refactor opportunities.
- **Scope:** In: profiling, architecture review, tech debt list; Out: major rewrites unless approved.
- **Acceptance:** Performance review documented; prioritized improvement plan; DoD referenced.
- **Dependencies/data:** `AI_first/projects/reporestructure/phases/phase02/`, profiling notes.
- **Outputs:** Benchmark notes, refactor backlog, recommended next phase.
- **Definition of Done:** Persona notes filled, DoD checklist referenced, validation steps recorded.

## Personas (record outputs; use `AI_first/docs/templates/review_checklists.md`)
- Project/Process Manager: Canonicalized data location to `data/processed/` (legacy `datasets/` and `rust_code/datasets/` marked reference-only); ensured BCO1 constants point to the canonical path; bug RPR-2026-01-003 closed and exports regenerated.
- Developer: Updated `src/starmaps/bco1.py` to default to `data/processed/updated_merged_star_exo_data.json`; added `data/README.md` for data layout and referenced it in `README.md`; ran BugMgmt exports to reflect closure.
- QA Lead: Verified BugMgmt exports render with the closed issue and no open items; spot-checked `AI_first/ui/bugmgmt_issues.html` regeneration via `issues.py`; BCO1 runtime not re-executed in this slice.
- Optional personas:
  - Performance/Cost:
    - Baseline review: data-load vectorization, text surface caching, click-only hit-testing, and info-surface caching already applied.
    - Primary hotspots: per-star update loop (position + magnitude + rect), full-scan visibility filtering, and random twinkle per update.
    - Priority improvements: precompute distance bands/masks, rotate only visible indices, reduce per-update randomness, avoid re-allocating rects, vectorize magnitude updates.
- DoD checklist reference: `AI_first/docs/templates/review_checklists.md`

## Plan
- Establish baseline runs and profiling approach.
- Capture hot spots and structural risks.
- Propose prioritized improvements and acceptance criteria.
- Close-out: canonicalize data paths, trim legacy assets, finalize perf tweaks, and update BugMgmt/PM docs.

## Execution notes
- Initial performance review completed with prioritized recommendations and acceptance targets (see below).
- BugMgmt/PM UI polish for accessibility and readability: refreshed typography/line height, added focus-visible outlines on interactive elements, made table headers sticky for long scrolls, improved small-screen filter layout, and cleared stale selections when filters hide the chosen issue.
- Closed dataset duplication risk (RPR-2026-01-003): set canonical dataset path to `data/processed/`, documented legacy `datasets/` and `rust_code/datasets/` as reference-only, and kept BCO1 pointed at `data/processed/updated_merged_star_exo_data.json`.
- Performance work (BCO1):
  - Default data path now canonical (`data/processed/updated_merged_star_exo_data.json`) via `JSON_FILE`.
  - Twinkle updates throttled to visible sprites only (`update_twinkle_for_visible` + `StarSprite.maybe_twinkle`) to avoid per-frame randomization and image churn.
  - Rotation path continues to touch only visible indices; twinkle work decoupled from rotation to keep the hot path lean.
- Archival: moved legacy datasets to `archive/legacy_datasets/` and left stubs with READMEs in `datasets/` and `rust_code/datasets/` pointing to `data/processed/`.
- Highest-impact targets:
  - Reduce visibility filtering to precomputed masks per filter and distance bands.
  - Rotate only visible points instead of the full star set.
  - Throttle twinkle updates to a fixed cadence instead of per update.
- Medium-impact targets:
  - Cache rects and update centers instead of recreating each frame.
  - Vectorize magnitude/index updates for visible stars.
  - Precompute per-star distance-to-origin and reuse for radius comparisons.
- Low-impact targets:
  - Avoid per-frame string formatting unless values change (already done).
  - Gate debug logging behind flags (already done).

## Validation
- Ran `python3 AI_first/scripts/issues.py list --format json --output AI_first/bugmgmt/exports/json/bugmgmt_issues.json`.
- Ran `python3 AI_first/scripts/issues.py list --format html --output AI_first/ui/bugmgmt_issues.html`.
- Manual review: BCO1 now defaults to `data/processed/updated_merged_star_exo_data.json`; legacy dataset paths documented as reference-only.
- Not run: `python3 scripts/run_bco1.py` after twinkle/rotation path tweaks (smoke test previously run before these changes).
- Open risk: final runtime validation deferred; run `python3 scripts/run_bco1.py` to confirm post-twinkle behavior when convenient.

## Documentation updates
- Added `data/README.md` (canonical data layout and legacy dirs marked reference-only).
- Updated root `README.md` data section to point to `data/processed` and warn against legacy dirs.
- Added archive/readme stubs in `datasets/` and `rust_code/datasets/` to redirect to canonical paths.

## Issues & lessons
- Performance review started; capture profiling traces (cProfile/line_profiler) before further refactors.
