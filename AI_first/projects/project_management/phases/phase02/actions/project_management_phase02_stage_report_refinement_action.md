# Stage Action (project_management_phase02_stage_report_refinement_action.md)

- **Phase/Stage:** Phase 02 — Report refinement.
- **Objective:** Analyze PM.html and user docs, then propose a more professional presentation and formatting plan.
- **Scope:** In: layout, typography, information architecture, link grouping; Out: automation or new frameworks.
- **Acceptance:** Proposal includes sections, data fields, and formatting rules; all recommendations stay within `AI_first/ui/style/bugmgmt.css`.
- **Dependencies/data:** `AI_first/ui/PM.html`, `AI_first/docs/user_docs/README.md`, `AI_first/docs/projectplan.md`.
- **Outputs:** Phase 02 proposal and acceptance criteria.
- **Definition of Done:** Persona notes filled and proposal documented.

## Personas (record outputs; use `AI_first/docs/templates/review_checklists.md`)
- Project/Process Manager:
- Developer:
- QA Lead:
- Optional personas (Product Manager, Repository Steward, Docs Expert, UI/Accessibility, Bug Triage, Automation/Tooling, Architect, Security, Ops/Observability, Performance/Cost, DBA):

## Analysis
- PM.html mixes summary, links, and action text in a single table; this makes scanning harder and hides status/ownership context.
- Project status relies on free-text actions; there is no explicit "Owner", "Last updated", or "Health" field.
- The top stats are static and visually similar to BugMgmt, but they do not map to the project plan or issues.
- Links are crowded in a single cell; users have to parse multiple long URLs to locate the key artifact.
- User docs are presented as a single README link with no indication of published documents, status, or latest revision.

## Proposal (professional presentation)
- **Portfolio header:** keep the hero header, but add a short "last updated" line and a "source of truth" note (Project Plan + BugMgmt).
- **Project cards (or grouped rows):** each project row should include:
  - Project name + purpose (secondary text).
  - Phase name + phase status.
  - Health pill (On Track / At Risk / Blocked) using existing badge colors.
  - Owner + last updated date.
  - Next actions as 1-2 bullets, not sentences.
- **Links grouped by type:** add a compact "Primary" link group (Summary, Action Plan, Stage Action) and a "Supporting" group (BugMgmt, User Docs).
- **User docs hub section:** list each user doc with status (Draft/Published), last updated date, and link to the PDF/TeX source.
- **Formatting rules:** use consistent row height, align text to baseline, keep secondary text in `muted small`, and limit action text to 2 lines.

## Plan
- Define new table columns and the standard fields for each project row.
- Add a user docs section that lists documents with status/last updated.
- Specify a maintenance checklist for keeping PM.html aligned with `AI_first/docs/projectplan.md`.

## Execution notes
- Implemented the professional PM.html layout with richer project status fields and link grouping.
- Added markdown viewer support (`AI_first/ui/markdown_viewer.html`, `AI_first/ui/assets/markdown.js`) for better .md rendering in the UI.
- Created project detail pages (`AI_first/ui/project_bugmgmt.html`, `AI_first/ui/project_project_management.html`) and updated user docs README formatting.

## Validation
- PM.html is readable in one screen without horizontal scrolling.
- Each project row includes owner, phase status, and next actions.
- User docs section lists at least one document with status + last updated.

## Documentation updates
- Update `AI_first/docs/projectplan.md` when Phase 02 is approved.

## Close-out
- Phase 02 approved; PM.html and user docs hub delivered.
- Closed on 2025-12-22.

## Issues & lessons
- Pending.
