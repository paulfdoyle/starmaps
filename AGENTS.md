# Repository Guidelines

## Project Structure & Module Organization
- `python_scripts/`: primary Python code and utilities (e.g., `main.py`, `Astro3D.py`, `graphics.py`), plus performance experiments in `python_scripts/performance_testing_for_coordinate_conversions/` and `python_scripts/artifacts/`.
- `datasets/`: JSON/CSV star and exoplanet data; many scripts read/write files here (e.g., `../datasets/updated_star_positions.csv`).
- `images/`: reference imagery and generated outputs.
- `rust_code/`: Rust prototypes (`star_field/`, `star_field_gpu/`) plus a copy of datasets used by the Rust code.
- `my-sky-tests/` and `Paper Draft/`: manual notes and paper assets (non-code).

## Build, Test, and Development Commands
- Python scripts expect to run from `python_scripts/` because of relative paths into `../datasets`:
  - `cd python_scripts && python3 main.py`
  - `cd python_scripts && python3 Astro3D.py` (or any other script entry point)
- Rust crates run from their crate directories:
  - `cd rust_code/star_field && cargo run`
  - `cd rust_code/star_field_gpu && cargo run`

## Coding Style & Naming Conventions
- Python uses 4-space indentation and snake_case for functions/variables; keep new module names consistent with nearby files (e.g., `data_handling.py`, `updatejson.py`).
- Rust follows standard Rust style; keep modules small and focused.
- Preserve relative-path conventions for data access (scripts often use `../datasets/...` from `python_scripts/`).

## Testing Guidelines
- No automated test framework is configured. Ad-hoc scripts live in `python_scripts/` (e.g., `test_pygame.py`, `test-starimages.py`) and notes in `my-sky-tests/`.
- If you add tests, document how to run them and keep the data files they touch in `datasets/`.

## Commit & Pull Request Guidelines
- The history only contains `initial upload`; there is no established commit convention. Use concise, imperative summaries like "Add GPU renderer for star field."
- PRs should describe changes, list any updated data files, and include screenshots/GIFs for rendering or visualization changes. Note performance impacts when relevant.

## Data & Assets
- Data files can be large; avoid manual edits unless required. If a script generates outputs, keep them in `datasets/` and mention the generator script in the PR.
