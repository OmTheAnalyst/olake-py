# olake-py
## Mission
`olake-py` is a Python-first companion to OLake that helps data engineers trigger and monitor OLake jobs from Python.  
It enables schema-aware CDC and Bronze → Silver promotion inside Databricks (Snowflake support will come later).

## Scope

### In-Scope (MVP)
- Trigger and monitor OLake jobs from Python.
- Apply CDC to Bronze Delta tables and promote to Silver in Databricks.
- Provide schema-change awareness and simple status/logs API.

### Non-Goals (for now)
- No Snowflake integration in Phase 0–1 (planned later).
- No full rewrite of OLake backend in Python (this is a companion library only).
- No advanced orchestration (handled by Databricks Jobs / external schedulers).

## Outcomes (MVP)
1. Start a CDC job from Python client and get a status response.
2. Run a CDC → Delta merge into Silver and validate results in Databricks.
3. View schema plan output from Python before applying changes.

## Engineering Conventions

- **Python Version**: 3.11
- **Package/Env Manager**: [uv](https://github.com/astral-sh/uv) (fast, modern replacement for pip/venv/poetry)
- **Linters/Tests (to be added in Phase 1)**:
  - ruff (linting & formatting)
  - mypy (type checking)
  - pytest (unit tests)
  - pre-commit (run checks before commit)
- **License**: Apache-2.0
- **Commit Style**: Conventional Commits  
  Examples:
  - `feat: add CDC start command`
  - `fix: handle schema drift in merge`
  - `docs: update README with conventions`
- **Branching Model**:
  - `main` → stable
  - feature branches: `feature/<short-name>`  
    Example: `feature/cdc-client`, `feature/add-tests`



