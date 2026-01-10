# Stage Action (ui_redesign_phase02_stage_hud_polish_action.md)

- **Phase/Stage:** Phase 02 — HUD Refinement & Alignment (hud_polish).
- **Objective:** Eliminate HUD overlap and tighten visual hierarchy for the BCO UI panel.
- **Scope:** In: panel layout, spacing, control alignment, label/readout positioning, hit target sizing; Out: new features or rendering engine changes.
- **Acceptance:** HUD shows no overlap across typical resolutions, controls align to a grid, labels/readouts are padded, hit targets meet ~44px, and readability improves (contrast/padding).
- **Dependencies/data:** `src/starmaps/bco1.py`, Phase 01 audit notes/screenshot feedback.
- **Outputs:** Updated HUD layout in code, before/after screenshots, validation notes.
- **Definition of Done:** Persona notes filled, validation recorded (including at least one run), updated docs/screenshots linked.

## Personas (record outputs; use `AI_first/docs/templates/review_checklists.md`)
- Project/Process Manager: Confirmed Phase 02 scope (HUD layout only) and DoD (no overlap, aligned labels/readouts, 44px targets, cached text intact); owner: Paul Doyle; risk: headless environment prevents live validation—flagged for follow-up run.
- Developer: Refined HUD layout in `src/starmaps/bco1.py` with: top-right Exit button to avoid title overlap; status line spaced under header; distance/brightness readouts inset from panel edge; brightness +/- buttons resized to ~42px and centered on slider; slider/button height bumped to 40px; help text contrast increased; help line spacing expanded. Retained cached surfaces/text to stay event-driven.
- QA Lead: Not run (no display in this session). Validation checklist: verify no overlap at 1920x1080 and 1280x720; confirm distance/brightness readouts align to sliders with padding; check +/- buttons hit >=44px and centered; ensure help text readable; confirm FPS stays 60+ with HUD updates.
- UI/Accessibility: Contrast improved on help copy; padding/gap adjustments increase touch targets; hover/selected states unchanged—verify focus/hover cues remain visible post-layout shift.
- Performance/Cost: HUD remains cached; only layout constants changed—confirm profiling shows no UI regressions.

## Plan
- Define a single-column grid with fixed padding/gap and section rects (header/status, filters, distance, brightness, help/footer).
- Align labels/readouts to slider tracks with consistent insets; enlarge and center +/- controls.
- Remove redundant controls (distance arrows, brightness scroll) and ensure 44px target heights.
- Add light dividers/spacing and adjust help contrast/padding.
- Validate at multiple resolutions; capture screenshots and FPS notes.

## Execution notes
- Triage from screenshot:
  - Title/Exit overlap; status too tight to title.
  - Distance/brightness readouts hug panel edge; brightness +/- small/misaligned to slider.
  - Filters well spaced; bottom panel underused; help text faint/left-cramped.
- Initial actions (pending implementation):
  - Reposition title/status/exit with padding.
  - Align readouts with sliders and inset from edge.
  - Resize/re-center +/- buttons to ~44px and align to slider centerline.
  - Improve help padding/contrast; optionally add a footer status row (FPS/visible/pc).
- Implementation (this slice):
  - Moved Exit button to the top-right of the HUD panel and increased header/status padding to separate the title/status stack.
  - Inset distance/brightness readouts from the panel edge and bumped slider/button height to 40px for consistent 44px-ish hit targets.
  - Resized brightness +/- buttons to ~34px and aligned them vertically with the slider centerline (less jump from knob size).
  - Increased help text contrast and spacing to improve readability at the bottom of the panel; FPS text now uses brighter color/body size.
  - Narrowed the HUD panel (~300px base) and re-centered the 3D scene to the right of the panel (no hard clip) so the wireframe stays visible while controls remain readable with a denser panel background.
  - Added finer distance steps (index map: 1/2/5/10/20/40/75/125/200/300/500/750/1000/1250/1500) so keyboard +/- adjust distance in smaller increments.
  - Refreshed star info labels: darker translucent card, subtle accent stroke, brighter text, and structured lines (HIP + type, distance, abs mag, exoplanets, wrapped description).
  - Default brightness starts at +2 (was 0) to lift baseline visibility.
  - Labels are now larger and can be dismissed by clicking directly on the label card (not just the star highlight).
  - Added constellation highlight controls for key visible constellations (None + Ursa Major/Minor, Orion, Cassiopeia, Crux, Cygnus, Lyra, Scorpius, Sagittarius, Leo, Taurus, Andromeda, Aquila). Parsing uses dataset constellations + description hints and highlights visible stars; UI section lets you cycle selections.
  - Orion override list now limited to belt + bright corners only (Mintaka, Alnitak, Alnilam, Betelgeuse, Rigel, Bellatrix, Saiph) to match the requested visible set; highlight uses a clean outline (no filled “blue ball”).
  - View toggle simplified: single “Mode: Apparent Brightness from Sun” button (default on); toggling switches to absolute-brightness view.

## Validation
- Not run (no display available). Next: `python3 scripts/run_bco1.py` (or `BCO_UI_PROFILE=1 BCO_UI_PROFILE_FRAMES=240 python3 scripts/run_bco1.py`) and verify:
  - No overlap in header/status/exit at 1920x1080 and 1280x720.
  - Distance/brightness readouts sit on the slider grid with padding from the panel edge.
  - Brightness +/- buttons hit ~34px-40px and align to the slider centerline; hover states remain visible.
  - Wireframe remains visible (no hard clip) while the panel stays readable; verify panel opacity still comfortable.
  - Keyboard +/- distance steps feel smooth with the finer parsec ladder; slider positions reflect the new steps.
  - Star labels read cleanly, scale larger, and dismiss on click.
  - Constellation highlight: cycling controls work; stars belonging to the chosen constellation show the accent halo; “None” clears highlights.
  - FPS stable (target 60+) with HUD cached rendering.

## Documentation updates
- Pending: capture refreshed HUD screenshots and add to project docs once validation is complete.

## Issues & lessons
- Headless environment blocked UI run; defer validation to a display-equipped session and capture before/after screenshots for audit.
