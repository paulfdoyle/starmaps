#!/usr/bin/env python3
"""Run the BCO1 star visualization."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from starmaps.bco1 import main


if __name__ == "__main__":
    main()
