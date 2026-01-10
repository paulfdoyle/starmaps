# Starmaps

Python-first star data visualization project. The current focus is migrating the initial BCO1 demo into a clean, professional repo structure.

## Quick Start (BCO1)
Run the BCO1 demo from the repo root:

```bash
python3 scripts/run_bco1.py
```

Outputs (if generated) are written to `assets/images/generated/`.

## Data
The BCO1 demo uses:
- `data/processed/updated_merged_star_exo_data.json`
- Legacy directories `datasets/` and `rust_code/datasets/` are reference-only; keep active datasets under `data/processed/` to avoid duplication.

## Layout
- `src/starmaps/`: core Python package (BCO1 module lives here).
- `scripts/`: runnable entry points.
- `data/`: datasets (`raw/`, `processed/`).
- `assets/`: images and static resources.
- `archive/`: legacy code retained for reference.
- `AI_first/`: process + PM/BugMgmt bundle.
