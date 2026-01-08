#!/usr/bin/env python3
"""Render PM dashboards (PM.html and project detail pages) from project docs."""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


PM_ROWS_START = "<!-- PROJECT_ROWS_START -->"
PM_ROWS_END = "<!-- PROJECT_ROWS_END -->"
PHASE_ROWS_START = "<!-- PHASE_ROWS_START -->"
PHASE_ROWS_END = "<!-- PHASE_ROWS_END -->"
PHASE_TEMPLATES_START = "<!-- PHASE_TEMPLATES_START -->"
PHASE_TEMPLATES_END = "<!-- PHASE_TEMPLATES_END -->"
EM_DASH = "\u2014"


@dataclass
class PhaseInfo:
    number: str
    name: str
    status: str
    completed: Optional[str]
    phase_def_path: Path
    action_plan_path: Path
    stage_actions: List[Path]


@dataclass
class ProjectInfo:
    slug: str
    status: str
    summary_path: Path
    purpose: str
    current_goal: str
    owner: str
    phases: List[PhaseInfo]
    active_phase: Optional[str]


def _normalize_status(value: Optional[str]) -> str:
    if not value:
        return ""
    text = value.strip().lower()
    if "complete" in text or "closed" in text:
        return "complete"
    if "planning" in text or "draft" in text:
        return "planning"
    if "active" in text or "in progress" in text or "in_progress" in text:
        return "active"
    return text.replace(" ", "_")


def _status_badge(status: str) -> tuple[str, str]:
    if status == "complete":
        return "Complete", "status-closed"
    if status == "planning":
        return "Planning", "status-open"
    return "Active", "status-in_progress"


def _extract_field(md_text: str, field: str) -> Optional[str]:
    pattern = re.compile(rf"^\s*-\s*\*\*{re.escape(field)}:\*\*\s*(.+)$", re.I | re.M)
    match = pattern.search(md_text)
    if not match:
        return None
    return match.group(1).strip().rstrip(".")


def _extract_list_block(md_text: str) -> str:
    lines = md_text.splitlines()
    block: List[str] = []
    collecting = False
    for line in lines:
        if re.match(r"^\s*[-*]\s+", line):
            collecting = True
        if collecting:
            if not line.strip():
                break
            block.append(line)
    return "\n".join(block)


def _render_inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<a href=\"\2\">\1</a>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def _render_list_summary(md_text: str) -> str:
    block = _extract_list_block(md_text)
    if not block:
        return '<ul class="muted small"></ul>'
    items: List[str] = []
    for line in block.splitlines():
        match = re.match(r"^\s*[-*]\s+(.*)$", line)
        if not match:
            continue
        content = _render_inline(match.group(1))
        items.append(f"<li>{content}</li>")
    return '<ul class="muted small">' + "".join(items) + "</ul>"


def _replace_between_markers(text: str, start_marker: str, end_marker: str, new_body: str) -> str:
    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker)
    if start_idx == -1 or end_idx == -1 or start_idx > end_idx:
        raise SystemExit(f"Missing marker block: {start_marker} ... {end_marker}")
    before = text[: start_idx + len(start_marker)]
    after = text[end_idx:]
    body = new_body.strip("\n")
    return f"{before}\n{body}\n{after}"


def _replace_summary_value(text: str, label: str, value: str) -> str:
    pattern = re.compile(
        rf'(<div class="summary-card">\s*<div class="muted small">{re.escape(label)}</div>\s*<div class="h6">)([^<]*)(</div>\s*</div>)',
        re.S,
    )
    return pattern.sub(rf"\g<1>{value}\g<3>", text, count=1)


def _replace_summary_item(text: str, label: str, value: str) -> str:
    if not value:
        return text
    pattern = re.compile(
        rf"(<li>\s*<strong>{re.escape(label)}:</strong>)([^<]*)(</li>)"
    )
    return pattern.sub(rf"\g<1> {html.escape(value)}\g<3>", text, count=1)


def _doc_link_from_md(md_path: Path, repo_root: Path) -> str:
    rel = md_path.relative_to(repo_root / "AI_first" / "projects")
    html_rel = Path("docs/projects") / rel
    return html_rel.with_suffix(".html").as_posix()


def _extract_stage_actions(action_plan_text: str, repo_root: Path) -> List[Path]:
    matches = re.findall(
        r"`(AI_first/projects/[^`]+/actions/[^`]+_action\.md)`",
        action_plan_text,
    )
    return [repo_root / match for match in matches]


def _parse_projectplan(projectplan_path: Path) -> List[dict]:
    text = projectplan_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    in_projects = False
    projects: List[dict] = []
    current: Optional[dict] = None
    for line in lines:
        if line.startswith("## Projects"):
            in_projects = True
            continue
        if line.startswith("## ") and in_projects:
            break
        if not in_projects:
            continue
        project_match = re.match(
            r"^- \*\*(?P<slug>[a-z0-9_]+)(?: \((?P<status>[^)]+)\))?\*\*",
            line.strip(),
        )
        if project_match:
            if current:
                projects.append(current)
            current = {
                "slug": project_match.group("slug"),
                "status": _normalize_status(project_match.group("status")),
                "summary_path": None,
                "phases": [],
            }
            continue
        if not current:
            continue
        summary_match = re.search(r"Summary:\s+`([^`]+)`", line)
        if summary_match:
            current["summary_path"] = summary_match.group(1)
            continue
        phase_match = re.match(
            rf"^\s+- Phase\s+(?P<num>\d+)\s+{re.escape(EM_DASH)}\s+(?P<name>[^()]+?)(?:\s+\((?P<status>[^)]+)\))?:\s+see\s+`(?P<path>[^`]+)`",
            line,
        )
        if phase_match:
            current["phases"].append(
                {
                    "number": phase_match.group("num").zfill(2),
                    "name": phase_match.group("name").strip(),
                    "status": _normalize_status(phase_match.group("status")),
                    "path": phase_match.group("path"),
                }
            )
    if current:
        projects.append(current)
    return projects


def _parse_project_summary(summary_path: Path) -> dict:
    result = {"purpose": "", "current_goal": "", "status": "", "owner": ""}
    if not summary_path.exists():
        return result
    for line in summary_path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^- \*\*(?P<label>[^*]+):\*\*\s*(?P<value>.*)$", line.strip())
        if not match:
            continue
        label = match.group("label").strip().lower()
        value = match.group("value").strip()
        if label == "purpose":
            result["purpose"] = value
        elif label == "current goal":
            result["current_goal"] = value
        elif label == "status":
            result["status"] = _normalize_status(value)
        elif label == "owner":
            result["owner"] = value
    return result


def _parse_status_completed(phase_def_path: Path, action_plan_path: Path) -> tuple[str, Optional[str]]:
    status = ""
    completed = None
    if phase_def_path.exists():
        text = phase_def_path.read_text(encoding="utf-8")
        status = _normalize_status(_extract_field(text, "Status"))
        completed = _extract_field(text, "Completed")
    if not status and action_plan_path.exists():
        text = action_plan_path.read_text(encoding="utf-8")
        status = _normalize_status(_extract_field(text, "Status"))
        if not completed:
            completed = _extract_field(text, "Completed")
    return status, completed


def _determine_active_phase(current_goal: str, phases: Iterable[PhaseInfo]) -> Optional[str]:
    if current_goal:
        match = re.search(r"Phase\s+(\d{1,2})", current_goal)
        if match:
            candidate = match.group(1).zfill(2)
            if any(phase.number == candidate for phase in phases):
                return candidate
    for phase in phases:
        if phase.status != "complete":
            return phase.number
    return phases[-1].number if phases else None


def _derive_next_actions(current_goal: str, project_status: str) -> List[str]:
    actions: List[str] = []
    if current_goal:
        goal = current_goal.strip()
        goal = re.sub(
            rf"^Phase\s+\d{{1,2}}\s*(?:{re.escape(EM_DASH)}|-)?\s*",
            "",
            goal,
            flags=re.I,
        )
        parts = [part.strip() for part in re.split(r"[;]", goal) if part.strip()]
        for part in parts:
            cleaned = part.rstrip(".")
            if cleaned.lower() in {"complete", "completed"}:
                continue
            actions.append(cleaned)
    if project_status == "complete":
        defaults = ["Maintain workflow, exports, and UI.", "Log new issues as they arise."]
    elif project_status == "planning":
        defaults = ["Define scope and success criteria.", "Populate the active stage action."]
    else:
        defaults = ["Execute active phase action plan.", "Update stage action with decisions/validation."]
    combined = actions + defaults
    result: List[str] = []
    seen = set()
    for item in combined:
        text = item.strip()
        if not text:
            continue
        if text[0].islower():
            text = text[0].upper() + text[1:]
        if not text.endswith("."):
            text += "."
        key = text.lower().rstrip(".")
        if key in seen:
            continue
        seen.add(key)
        result.append(text)
        if len(result) == 2:
            break
    return result if len(result) == 2 else (result + defaults)[:2]


def _count_open_bugs(issues_path: Path) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    if not issues_path.exists():
        return counts
    for line in issues_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if str(payload.get("status", "")).lower() != "open":
            continue
        project = str(payload.get("project", "")).strip()
        if not project:
            continue
        counts[project] = counts.get(project, 0) + 1
    return counts


def _build_projects(repo_root: Path, projectplan_path: Path) -> List[ProjectInfo]:
    raw_projects = _parse_projectplan(projectplan_path)
    projects: List[ProjectInfo] = []
    for raw in raw_projects:
        slug = raw["slug"]
        summary_path = repo_root / raw["summary_path"] if raw.get("summary_path") else None
        if not summary_path:
            raise SystemExit(f"Missing summary path for project {slug} in {projectplan_path}")
        summary = _parse_project_summary(summary_path)
        project_status = raw["status"] or summary["status"] or "active"
        phases: List[PhaseInfo] = []
        for phase_data in raw["phases"]:
            number = phase_data["number"]
            name = phase_data["name"]
            phase_root = repo_root / "AI_first" / "projects" / slug / "phases" / f"phase{number}"
            phase_def_path = phase_root / "phase_definition.md"
            action_plan_path = phase_root / f"action_plan_phase{number}.md"
            doc_status, completed = _parse_status_completed(phase_def_path, action_plan_path)
            status = phase_data["status"] or doc_status
            stage_actions: List[Path] = []
            if action_plan_path.exists():
                stage_actions = _extract_stage_actions(action_plan_path.read_text(encoding="utf-8"), repo_root)
            if not stage_actions:
                actions_dir = phase_root / "actions"
                if actions_dir.exists():
                    stage_actions = sorted(actions_dir.glob("*.md"))
            phases.append(
                PhaseInfo(
                    number=number,
                    name=name,
                    status=status,
                    completed=completed,
                    phase_def_path=phase_def_path,
                    action_plan_path=action_plan_path,
                    stage_actions=stage_actions,
                )
            )
        active_phase = _determine_active_phase(summary["current_goal"], phases)
        for phase in phases:
            if phase.status:
                continue
            if active_phase and phase.number == active_phase and project_status != "complete":
                phase.status = "active"
            elif project_status == "complete":
                phase.status = "complete"
            else:
                phase.status = "planning"
        projects.append(
            ProjectInfo(
                slug=slug,
                status=project_status,
                summary_path=summary_path,
                purpose=summary["purpose"],
                current_goal=summary["current_goal"],
                owner=summary["owner"] or "unassigned",
                phases=phases,
                active_phase=active_phase,
            )
        )
    return projects


def _render_pm_rows(projects: Iterable[ProjectInfo]) -> str:
    rows: List[str] = []
    indent = "            "
    for project in projects:
        active_phase = next(
            (phase for phase in project.phases if phase.number == project.active_phase), None
        )
        if active_phase:
            phase_label = f"Phase {active_phase.number} {EM_DASH} {active_phase.name}"
        elif project.phases:
            phase_label = f"Phase {project.phases[-1].number} {EM_DASH} {project.phases[-1].name}"
        else:
            phase_label = "TBD"
        status_label, status_class = _status_badge(project.status)
        health_label = "Complete" if project.status == "complete" else "On Track"
        health_class = "status-closed"
        actions = _derive_next_actions(project.current_goal, project.status)
        description = project.purpose or "Project overview."
        description_html = _render_inline(description)
        last_updated = _latest_completed_date(project.phases) or "TBD"
        row_lines = [
            f'{indent}<tr data-link="project_{project.slug}.html" tabindex="0" role="button" aria-label="Open {project.slug} project details">',
            f"{indent}  <td>",
            f'{indent}    <a class="fw" href="project_{project.slug}.html">{project.slug}</a>',
            f'{indent}    <div class="muted small">{description_html}</div>',
            f"{indent}  </td>",
            f"{indent}  <td>{html.escape(phase_label)}</td>",
            f'{indent}  <td><span class="badge {status_class}">{status_label}</span></td>',
            f'{indent}  <td><span class="badge {health_class}">{health_label}</span></td>',
            f"{indent}  <td>{html.escape(project.owner)}</td>",
            f"{indent}  <td>{last_updated}</td>",
            f'{indent}  <td class="muted small">',
            f"{indent}    <div>{_render_inline(actions[0])}</div>",
            f"{indent}    <div>{_render_inline(actions[1])}</div>",
            f"{indent}  </td>",
            f"{indent}</tr>",
        ]
        rows.append("\n".join(row_lines))
    return "\n".join(rows)


def _latest_completed_date(phases: Iterable[PhaseInfo]) -> Optional[str]:
    dates = [phase.completed for phase in phases if phase.completed]
    dates = [date for date in dates if re.match(r"^\d{4}-\d{2}-\d{2}$", date)]
    return max(dates) if dates else None


def _update_pm_html(
    pm_path: Path,
    projects: List[ProjectInfo],
    open_bugs: Dict[str, int],
    dry_run: bool,
) -> bool:
    text = pm_path.read_text(encoding="utf-8")
    rows = _render_pm_rows(projects)
    updated = _replace_between_markers(text, PM_ROWS_START, PM_ROWS_END, rows)
    updated = _replace_count(updated, "projects", len(projects))
    active_count = sum(
        1
        for project in projects
        if project.active_phase
        and any(
            phase.number == project.active_phase and phase.status != "complete" for phase in project.phases
        )
    )
    updated = _replace_count(updated, "active-phases", active_count)
    total_open = sum(open_bugs.values())
    updated = _replace_count(updated, "open-bugs", total_open)
    if dry_run:
        print(f"[dry-run] update {pm_path}")
        return False
    pm_path.write_text(updated, encoding="utf-8")
    return True


def _replace_count(text: str, key: str, value: int) -> str:
    pattern = re.compile(rf'(data-count="{re.escape(key)}">)(\d+)(</div>)')
    return pattern.sub(rf"\g<1>{value}\3", text, count=1)


def _render_phase_rows(project: ProjectInfo, repo_root: Path) -> str:
    rows: List[str] = []
    indent = "            "
    for phase in project.phases:
        status_label, status_class = _status_badge(phase.status)
        last_updated = phase.completed or "TBD"
        phase_label = f"Phase {phase.number} {EM_DASH} {phase.name}"
        row_lines = [
            f'{indent}<tr data-phase="{html.escape(phase_label)}"',
            f'{indent}    data-phase-def-id="phase{phase.number}-def"',
            f'{indent}    data-action-plan-id="phase{phase.number}-plan"',
            f'{indent}    data-stage-action-id="phase{phase.number}-action"',
            f'{indent}    tabindex="0" role="button" aria-label="View Phase {phase.number} details">',
            f"{indent}  <td>{html.escape(phase_label)}</td>",
            f'{indent}  <td><span class="badge {status_class}">{status_label}</span></td>',
            f"{indent}  <td>{last_updated}</td>",
            f"{indent}</tr>",
        ]
        rows.append("\n".join(row_lines))
    return "\n".join(rows)


def _render_phase_templates(project: ProjectInfo) -> str:
    indent = "    "
    templates: List[str] = []
    for phase in project.phases:
        phase_def_body = _read_summary_body(phase.phase_def_path)
        action_plan_body = _read_summary_body(phase.action_plan_path)
        if phase.stage_actions:
            stage_action_body = _read_summary_body(phase.stage_actions[0])
        else:
            stage_action_body = '<ul class="muted small"><li><strong>Stage Action:</strong> TBD.</li></ul>'
        templates.append(_wrap_template(f"phase{phase.number}-def", phase_def_body, indent))
        templates.append(_wrap_template(f"phase{phase.number}-plan", action_plan_body, indent))
        templates.append(_wrap_template(f"phase{phase.number}-action", stage_action_body, indent))
    return "\n".join(templates)


def _read_summary_body(md_path: Path) -> str:
    if not md_path.exists():
        return '<ul class="muted small"><li><strong>Missing:</strong> file not found.</li></ul>'
    return _render_list_summary(md_path.read_text(encoding="utf-8"))


def _wrap_template(template_id: str, body: str, indent: str) -> str:
    body_indented = "\n".join(f"{indent}  {line}" for line in body.splitlines())
    return f'{indent}<template id="{template_id}">\n{body_indented}\n{indent}</template>'


def _update_project_detail(
    project: ProjectInfo,
    html_path: Path,
    repo_root: Path,
    open_bugs: Dict[str, int],
    dry_run: bool,
) -> bool:
    if not html_path.exists():
        print(f"[skip] missing {html_path}")
        return False
    text = html_path.read_text(encoding="utf-8")
    phase_rows = _render_phase_rows(project, repo_root)
    text = _replace_between_markers(text, PHASE_ROWS_START, PHASE_ROWS_END, phase_rows)
    templates = _render_phase_templates(project)
    text = _replace_between_markers(text, PHASE_TEMPLATES_START, PHASE_TEMPLATES_END, templates)
    text = _replace_summary_value(text, "Phases", str(len(project.phases)))
    if "Open Bugs" in text:
        text = _replace_summary_value(text, "Open Bugs", str(open_bugs.get(project.slug, 0)))
    if "Active Phase" in text:
        active_label = "Complete"
        if project.active_phase and project.status != "complete":
            active_label = f"Phase {project.active_phase}"
        text = _replace_summary_value(text, "Active Phase", active_label)
    if "Status" in text:
        status_label, _ = _status_badge(project.status)
        text = _replace_summary_value(text, "Status", status_label)
    text = _replace_summary_item(text, "Purpose", project.purpose)
    text = _replace_summary_item(text, "Current Goal", project.current_goal)
    text = _replace_summary_item(text, "Status", _status_badge(project.status)[0])
    text = _replace_summary_item(text, "Owner", project.owner)
    if dry_run:
        print(f"[dry-run] update {html_path}")
        return False
    html_path.write_text(text, encoding="utf-8")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render PM dashboards from project docs")
    parser.add_argument(
        "--projectplan",
        type=Path,
        default=Path("AI_first/docs/projectplan.md"),
        help="Project plan source markdown",
    )
    parser.add_argument(
        "--issues",
        type=Path,
        default=Path("AI_first/bugmgmt/issues/issues.jsonl"),
        help="BugMgmt issues source jsonl",
    )
    parser.add_argument(
        "--pm",
        type=Path,
        default=Path("AI_first/ui/PM.html"),
        help="PM dashboard HTML output",
    )
    parser.add_argument(
        "--ui",
        type=Path,
        default=Path("AI_first/ui"),
        help="UI root containing project_<project>.html",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    projectplan_path = (repo_root / args.projectplan).resolve()
    issues_path = (repo_root / args.issues).resolve()
    pm_path = (repo_root / args.pm).resolve()
    ui_root = (repo_root / args.ui).resolve()

    projects = _build_projects(repo_root, projectplan_path)
    open_bugs = _count_open_bugs(issues_path)

    updated_files: List[Path] = []
    if _update_pm_html(pm_path, projects, open_bugs, args.dry_run):
        updated_files.append(pm_path)

    for project in projects:
        detail_path = ui_root / f"project_{project.slug}.html"
        if _update_project_detail(project, detail_path, repo_root, open_bugs, args.dry_run):
            updated_files.append(detail_path)

    if args.dry_run:
        return
    if updated_files:
        print("Updated:")
        for path in updated_files:
            print(f"  - {path}")
    else:
        print("No updates needed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
