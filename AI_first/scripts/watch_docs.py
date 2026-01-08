#!/usr/bin/env python3
"""Watch markdown under AI_first/docs and AI_first/projects, auto-rendering on change."""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def _latest_mtime(root: Path) -> float:
    latest = 0.0
    if not root.exists():
        return latest
    for path in root.rglob("*.md"):
        try:
            latest = max(latest, path.stat().st_mtime)
        except FileNotFoundError:
            continue
    return latest


def _render_once(repo_root: Path) -> int:
    script_path = repo_root / "AI_first" / "scripts" / "render_docs.py"
    result = subprocess.run([sys.executable, str(script_path)])
    return result.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Watch markdown and auto-render docs")
    parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    support_root = repo_root / "AI_first" / "docs"
    projects_root = repo_root / "AI_first" / "projects"
    last_seen = max(_latest_mtime(support_root), _latest_mtime(projects_root))

    print("Watching docs for changes (Ctrl+C to stop)...")
    try:
        while True:
            time.sleep(args.interval)
            latest = max(_latest_mtime(support_root), _latest_mtime(projects_root))
            if latest > last_seen:
                print("Docs changed. Rendering AI_first/ui/docs...")
                code = _render_once(repo_root)
                if code != 0:
                    print(f"Render failed with exit code {code}.")
                last_seen = latest
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()
