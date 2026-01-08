# Template Release Checklist

- [ ] Validation run completed in scratch copy (commands recorded in Phase 03 validation action); hashes stable; JSON parse ok.
- [ ] UI pages load via file:// with bundled assets (bugmgmt_issues.html); report_base.html visually checked.
- [ ] README.md updated with quickstart, BugMgmt toggle, process/persona overview, sample project pointer, PII warning.
- [ ] Adoption guide added (AI_first/docs/template_howto.md) with steps to start a new project and use templates.
- [ ] Paths/commands verified (data/export/UI dirs configurable in AI_first/scripts/issues.py via flags/env).
- [ ] Sample data is PII-free; deterministic ordering noted.
- [ ] Links resolve: AI_first/docs/process.md, projectplan.md, personas.md, templates/, sample project, BugMgmt commands, UI template.
- [ ] Issues/lessons logged if any defects found; toggle guidance included for skipping BugMgmt.
- [ ] Ready for drop-in use: ensure AI_first is self-contained and copyable as a single folder.
