# Personas (Template)

Use these prompts when reviewing project phases or change proposals. Primary personas are expected for most work; optional personas are used only when the scope warrants it. Each persona should produce concrete outputs in this repo.

## Primary Personas

### Project Creator/Owner
- Purpose: initialize the template for a new repo and project.
- When to use: first-time setup, new project creation.
- Inputs: desired project name, purpose, owner, prefix.
- Outputs: project name/purpose, phase list, files to create/update (projectplan, project summary, phases).
- Prompt: "Act as Project Creator/Owner. Confirm project name, purpose, owner, prefix, and initial phases to create."

### Project/Process Manager
- Purpose: clarify phase/stage, next steps, owners, risks, handoffs.
- When to use: weekly updates, phase transitions.
- Inputs: `AI_first/docs/projectplan.md`, project phase docs.
- Outputs: next actions, dates, owners, dependency risks.
- Prompt: "Act as Project/Process Manager. List next steps, owners, risks, and handoffs."

### Product Manager
- Purpose: define acceptance criteria and scope boundaries.
- When to use: feature scope, phase planning.
- Inputs: project summary, action plan, user docs.
- Outputs: acceptance criteria, in/out of scope, open questions.
- Prompt: "Act as Product Manager. Provide acceptance criteria and scope boundaries."

### Repository Steward
- Purpose: protect the template structure and AI_first/project separation.
- When to use: repo restructuring, onboarding, or new project creation.
- Inputs: repo layout, README, AI_first docs.
- Outputs: structure changes, path decisions, README updates.
- Prompt: "Act as Repository Steward. Ensure AI_first tooling stays separate from product work."

### Developer
- Purpose: implementation notes and technical constraints.
- When to use: any code/script/UI change.
- Inputs: affected files and scripts.
- Outputs: design notes, risks, tech debt, logging/telemetry needs.
- Prompt: "Act as Developer. Summarize implementation risks and needed changes."

### QA Lead
- Purpose: identify risks, edge cases, validation signals, and regression coverage.
- When to use: UI or script changes, release readiness.
- Inputs: BugMgmt UI, PM.html, scripts.
- Outputs: test scenarios, pass/fail criteria, regression checklist.
- Prompt: "Act as QA Lead. List edge cases, acceptance signals, and regression checks."

## Optional Personas

### Product Manager
- Purpose: define acceptance criteria and scope boundaries.
- When to use: feature scope, phase planning.
- Inputs: project summary, action plan, user docs.
- Outputs: acceptance criteria, in/out of scope, open questions.
- Prompt: "Act as Product Manager. Provide acceptance criteria and scope boundaries."

### Repository Steward
- Purpose: protect the template structure and AI_first/project separation.
- When to use: repo restructuring, onboarding, or new project creation.
- Inputs: repo layout, README, AI_first docs.
- Outputs: structure changes, path decisions, README updates.
- Prompt: "Act as Repository Steward. Ensure AI_first tooling stays separate from product work."

### Docs Expert
- Purpose: keep docs accurate, consistent, and linked.
- When to use: any process or structure change.
- Inputs: `AI_first/docs` and `AI_first/projects` docs.
- Outputs: doc updates needed, broken link fixes, clarity edits.
- Prompt: "Act as Docs Expert. List doc updates and link fixes."

### UI/Accessibility
- Purpose: usability, accessibility, and style consistency checks.
- When to use: UI changes or new pages.
- Inputs: PM.html, BugMgmt UI, CSS.
- Outputs: UI issues, a11y fixes, style consistency notes.
- Prompt: "Act as UI/Accessibility. Identify usability and a11y issues."

### Bug Triage
- Purpose: ensure issues are complete and consistent.
- When to use: after logging or updating bugs.
- Inputs: `AI_first/bugmgmt/issues/issues.jsonl`.
- Outputs: missing fields, invalid prefixes, owner gaps.
- Prompt: "Act as Bug Triage. Validate IDs, required fields, and owners."

### Automation/Tooling
- Purpose: keep exports and rendered docs in sync.
- When to use: after doc or issue updates.
- Inputs: `AI_first/scripts/*.py`, UI exports.
- Outputs: required command list to refresh UI/docs.
- Prompt: "Act as Automation/Tooling. List required commands to refresh outputs."

### Architect
- Purpose: cross-boundary risks and redesign needs.
- When to use: major structure or workflow changes.
- Inputs: overall workflow, scripts, UI.
- Outputs: architecture risks, acceptance conditions, constraints.
- Prompt: "Act as Architect. Identify boundary risks and acceptance conditions."

### Security
- Purpose: threats, secrets/PII handling, and mitigations.
- When to use: new data flows, scripts, or exports.
- Inputs: scripts and data stores.
- Outputs: risks, mitigations, logging hygiene notes.
- Prompt: "Act as Security. Identify threats and mitigations."

### Ops/Observability
- Purpose: operational readiness and monitoring.
- When to use: automation or workflow changes.
- Inputs: scripts, run steps, outputs.
- Outputs: runbook gaps, alerts/metrics needs, rollback notes.
- Prompt: "Act as Ops/Observability. Identify runbook or monitoring gaps."

### Performance/Cost
- Purpose: perf or cost risks.
- When to use: only if scale or cost matters.
- Inputs: data size, runtime steps.
- Outputs: benchmarks and acceptance thresholds.
- Prompt: "Act as Performance/Cost. Note perf risks and thresholds."

### DBA
- Purpose: data integrity and schema impacts.
- When to use: only if a database is introduced.
- Inputs: data model, migrations.
- Outputs: integrity risks, backup/rollback needs.
- Prompt: "Act as DBA. Note schema and integrity risks."
