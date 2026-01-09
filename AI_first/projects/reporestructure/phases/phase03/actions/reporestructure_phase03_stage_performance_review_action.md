# Stage Action (reporestructure_phase03_stage_performance_review_action.md)

- **Phase/Stage:** Phase 03 — Performance & Technical Review (performance_review).
- **Objective:** Review performance and technical structure; document refactor opportunities.
- **Scope:** In: profiling, architecture review, tech debt list; Out: major rewrites unless approved.
- **Acceptance:** Performance review documented; prioritized improvement plan; DoD referenced.
- **Dependencies/data:** `AI_first/projects/reporestructure/phases/phase02/`, profiling notes.
- **Outputs:** Benchmark notes, refactor backlog, recommended next phase.
- **Definition of Done:** Persona notes filled, DoD checklist referenced, validation steps recorded.

## Personas (record outputs; use `AI_first/docs/templates/review_checklists.md`)
- Project/Process Manager:
- Developer:
- QA Lead:
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

## Execution notes
- Initial performance review completed with prioritized recommendations and acceptance targets (see below).
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
- Pending.

## Documentation updates
- Pending.

## Issues & lessons
- Performance review started; capture profiling traces (cProfile/line_profiler) before further refactors.
