# Stage Action (ui_redesign_phase01_stage_audit_action.md)

- **Phase/Stage:** Phase 01 — Discovery & Direction (audit).
- **Objective:** Define scope, workflow, and expectations for UI Redesign.
- **Scope:** In: planning docs and acceptance criteria; Out: implementation.
- **Acceptance:** Persona notes recorded; scope documented; DoD referenced.
- **Dependencies/data:** `AI_first/docs/process.md`, `AI_first/docs/projectplan.md`, `AI_first/projects/ui_redesign/project_summary_ui_redesign.md`
- **Outputs:** Updated phase/stage docs and any related process updates.
- **Layout proposal summary:** Left HUD panel (320-360px) with grouped sections (header, filters, distance, brightness, toggles, help); unified controls and cached UI surfaces.
- **Layout proposal highlights:** Filters and toggles grouped top-to-bottom; distance/brightness controls use a single slider each with numeric readout.
- **Interaction model:** Primary mouse controls with optional +/- micro-controls; keyboard/scroll hints live in a collapsible help footer.
- **Performance approach:** Cache HUD panels and labels; re-render dynamic values only on change.
- **UI spec draft:** Palette, typography scale, component sizes, layout grid, and interaction mapping.
- **Definition of Done:** Persona notes filled, DoD checklist referenced, validation steps recorded.

## Personas (record outputs; use `AI_first/docs/templates/review_checklists.md`)
- Project/Process Manager:
  - Scope focus: BCO stars UI in `src/starmaps/bco1.py` (entry `scripts/run_bco1.py`).
  - Stage output: UI audit notes, criteria for professional look and performance, and a layout proposal next.
- Developer:
  - Current UI controls: menu buttons, parsec arrow buttons, parsec slider, brightness slider, keyboard and scroll bindings.
  - UI drawing is direct to the star field each frame with fixed coordinates and hard-coded font sizing.
  - Interaction paths are duplicated (keys, scroll, sliders), which increases maintenance and UX inconsistency risk.
- QA Lead:
  - Verify consistent control behavior across mouse, keyboard, and scroll.
  - Confirm UI elements remain readable and clickable across resolutions.
  - Confirm performance targets (60+ FPS) with UI changes and no regressions in star rendering.
- Optional personas (Product Manager, Repository Steward, Docs Expert, UI/Accessibility, Bug Triage, Automation/Tooling, Architect, Security, Ops/Observability, Performance/Cost, DBA):
  - UI/Accessibility: legible type scale, contrast-safe overlay panel, 44px hit targets, clear hover/selected state.
  - Performance/Cost: cached UI surfaces and event-driven redraws; minimize per-frame allocations.

## Plan
- Confirm scope: BCO stars UI in `src/starmaps/bco1.py` only.
- Capture current control map and rendering paths for buttons and sliders.
- Define professional UI criteria and performance criteria.
- Draft a panel-based layout proposal with consistent interactions and text labels.

## Execution notes
- BCO UI audit (current use):
  - Menu buttons: fixed-position rectangles (filter menu) with hover/selected state; no panel background, so readability depends on star-field density.
  - Parsec control: arrow buttons plus a horizontal slider, fixed coordinates, no DPI scaling.
  - Brightness control: slider plus scroll wheel and R/T keys; visual label is separate and not co-located with slider.
  - UI text: hard-coded font (Consolas, size 14) and fixed placements.
- Graphics engine in use:
  - Pygame software rendering with sprite-based stars and additive blending (`CustomSpriteGroup.draw`).
  - Precomputed star surface variants for twinkle; Numba rotation and visibility masks for visible stars.
  - UI is redrawn every frame; star updates are gated by rotation/visibility/brightness changes.
  - Full-screen/no-frame window across monitors with fixed UI coordinates.
- Criteria for a more professional UI:
  - Responsive layout: panels and controls anchored to edges; no fixed pixel-only positions.
  - Visual hierarchy: semi-opaque HUD panel, grouped controls, consistent spacing and labels.
  - Consistent interaction: one primary control per action (slider or buttons) with clear state.
  - Readability: typography scale (16/20/24), consistent stroke weights, contrast-safe colors.
  - Affordance: 44px hit targets and visible hover/active states.
- Criteria for UI performance:
  - Frame budget: target 60+ FPS; UI render under 1 ms, star render and update under 15 ms.
  - Event-driven UI redraw: cache UI surfaces, update only on state change (filter/slider/hover).
  - Avoid per-frame allocations for UI text or surfaces.
- Layout proposal (BCO stars UI):
  - Layout: left-side HUD panel (320-360px width) with semi-opaque background and subtle border; star field remains full-bleed.
  - Sections:
    - Header: title "BCO Star Map" + compact status row (FPS, visible stars, current parsecs).
    - Filters: vertical button stack with selected state and short labels; include "All Stars" default.
    - Distance: single slider with numeric readout; keep arrow buttons optional as +/- micro-controls.
    - Brightness: single slider with +/- buttons and current offset readout.
    - Toggles: frame, sun, labels, optimize (icon + label).
    - Help: inline key/scroll hints in a collapsible footer.
  - Typography & spacing: base 16px, section labels 14px, header 20-22px; 12-16px padding; 10-12px gaps.
  - Interaction model: unify to one primary input per control; hover/active states consistent across buttons and sliders.
  - Rendering: cache panel background and static labels; re-render dynamic values only on change.
- UI spec draft (BCO HUD):
  - Layout grid:
    - `ui_scale = clamp(min(w / 1280, h / 720), 0.85, 1.2)`.
    - Panel width: `int(340 * ui_scale)`; panel height: `int(h * 0.88)`.
    - Panel inset: `int(16 * ui_scale)`; section spacing: `int(14 * ui_scale)`; control padding: `int(10 * ui_scale)`.
  - Typography:
    - Font: include `assets/fonts/SpaceGrotesk-Regular.ttf` and `SpaceGrotesk-Medium.ttf` (fallback to system sans).
    - Sizes: header 22, section 16, body 14, micro 12 (all scaled by `ui_scale`).
  - Color palette:
    - Background: `rgb(6, 10, 14)`; panel: `rgba(12, 16, 22, 200)`.
    - Text primary: `rgb(230, 236, 244)`; text secondary: `rgb(168, 178, 191)`.
    - Accent: `rgb(76, 201, 240)`; accent-alt: `rgb(98, 245, 156)`.
    - Border: `rgba(255, 255, 255, 40)`.
  - Buttons:
    - Height 36-40px; radius 8; 1px border.
    - States: default (border only), hover (border + text accent), selected (fill accent at 20% opacity).
  - Sliders:
    - Track height 4px; knob radius 8px; numeric readout to the right.
    - Distance slider maps to `index_parsecs`; brightness slider maps to `BRIGHTNESS_MIN/MAX`.
  - Toggles:
    - Row of 2x2 toggles or vertical stack; icon + label; on/off uses accent fill and check mark.
  - Interaction mapping:
    - Filters: single click; keyboard shortcuts optional (1-4).
    - Distance: slider drag; optional +/- buttons step `index_parsecs`.
    - Brightness: slider drag; scroll wheel adjusts when cursor over slider.
    - Help: collapsible footer shows key/scroll hints.
  - Rendering approach:
    - Pre-render static labels and panel background surfaces.
    - Re-render only on state change (hover, selection, values).
- Implementation progress:
  - Added HUD panel rendering, UI palette, and scalable layout in `src/starmaps/bco1.py`.
  - Updated menu/button/slider styling to use the new palette and typography.
  - Positioned header, filters label, distance/brightness labels, and help text inside the HUD.
  - Unified distance control to discrete parsec steps across slider, arrow buttons, and +/- keys.
  - Brightness slider now supports drag/hover scroll only when the cursor is over the slider.
  - Slider rendering uses shared track/knob component with active-state styling.
  - Cached HUD static surface and pre-rendered button/arrow surfaces; per-frame UI work now mostly blits.
  - Added brightness +/- micro-controls and button cache surfaces.
  - Added UI profiling hooks gated by `BCO_UI_PROFILE` and optional auto-exit frame count.

## Validation
- Pending: capture a profiling run with UI and frame averages.
- Run: `BCO_UI_PROFILE=1 BCO_UI_PROFILE_FRAMES=300 python3 scripts/run_bco1.py`
- Record: average UI ms, average frame ms, FPS range, and dataset size used.
- Note: automated run attempt here aborted (Signal 6); run locally with a display.

## Documentation updates
- Pending.

## Issues & lessons
- None logged yet.
