# Phase 02 Action Plan — HUD Refinement & Alignment

- **Phase:** see `AI_first/projects/ui_redesign/phases/phase02/phase_definition.md`.
- **Stage list:**
  - HUD polish stage -> `AI_first/projects/ui_redesign/phases/phase02/actions/ui_redesign_phase02_stage_hud_polish_action.md`
- **Objective:** Align HUD controls, remove overlap, and improve readability/affordance for the BCO UI.
- **Scope/files:** In: `src/starmaps/bco1.py` HUD layout, padding, alignment, control sizing, label/readout positioning; Out: rendering engine changes.
- **Dependencies:** Phase 01 audit complete.
- **Risks/assumptions:** Fixed-width panel; must retain 60+ FPS and avoid per-frame allocations.
- **Persona actions:** Project/Process Manager → Developer → QA Lead; add UI/Accessibility and Performance/Cost as needed.
- **Validation:** HUD renders without overlap at common resolutions; controls align to a grid; readouts padded; hit targets >= 44px; brightness/distance interactions consistent.
- **Rollback:** Revert HUD layout changes if performance or readability regresses.
- **Ready checklist:** Audit notes available; screenshot feedback captured.
- **Done checklist:** Stage action populated with persona notes, validation results, and updated HUD screenshots.
