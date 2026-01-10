# Data layout and canonical paths

- Canonical datasets live under `data/processed/`. The current primary file is `data/processed/updated_merged_star_exo_data.json`.
- Raw sources belong in `data/raw/`; keep any derived outputs in `data/processed/` and make generation steps deterministic.
- Legacy directories `datasets/` and `rust_code/datasets/` are retained for reference only. Do not add new files there and avoid copying them into the active tree; archive them when no longer needed.
- New scripts should resolve paths from the repo root (e.g., `Path(__file__).resolve().parents[2] / "data" / "processed"`), not from the legacy `datasets/` locations.
