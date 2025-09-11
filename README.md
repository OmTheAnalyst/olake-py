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


## Secrets Policy

- **Local Development**: use a `.env` file with required keys. Never commit real values.  
- **CI/CD (GitHub)**: store secrets in GitHub Secrets.  
- **Databricks**: store secrets in Databricks Secrets (workspace scope).  
- A `.env.example` file is provided as a template — fill values locally or in CI/CD as appropriate.

## Databricks Prereqs

- **Workspace Access**: Confirm you have a Databricks workspace (Free Edition is fine).
- **Cluster**: Create a single cluster (DBR 14 LTS or 15 LTS recommended).
- **Personal Access Token (PAT)**: Generate a PAT and store it in Databricks Secrets (note the last-8 chars for tracking).
- **Silver Target for MVP**: Delta tables stored in DBFS (simplest option).  
  - Cloud storage Delta can be considered later once credentials are wired.  
- **Workspace Folder for Examples**: Use `/Repos/olake-py/examples` as the default location.


## Sandbox Plan

- **Services & Ports**:
  - OLake API → 8080
  - Postgres → 5432
  - MinIO → 9000 (API), 9001 (console)
- **Docker Volumes**:
  - Use a single root folder: `sandbox/.data/`
- **Services**:
  - MinIO (for S3)
  - Postgres (for metadata)
  - Optional: Nessie (for Iceberg catalog) — not required for MVP


## Definition of Done – Phase 0

- Mission, Scope, and Outcomes documented in README.
- Engineering Conventions (Python version, packaging, branch/commit style) documented.
- GitHub hygiene set up:
  - Branch protection on `main`
  - Labels created
  - Project board created
  - Issue & PR templates in place
  - CODEOWNERS added
- Secrets Policy documented and `.env.example` committed.
- Repo skeleton structure created with placeholder READMEs.
- Databricks prerequisites documented.
- Sandbox Plan documented.



