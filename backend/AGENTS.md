# Repository Guidelines

## Project Structure & Module Organization
`app/` contains the FastAPI service. Keep HTTP routes in `app/api/`, shared business logic in `app/services/`, auth helpers in `app/core/`, Pydantic contracts in `app/models/`, and database code in `app/db/`. The application entrypoint is `app/main.py`; settings are loaded from `app/config.py`; the local SQLite file is `mental_health.db`. Put one-off operational scripts in `scripts/`, for example `scripts/ingest_pinecone.py`.

## Build, Test, and Development Commands
This repo does not currently check in a `requirements.txt` or `pyproject.toml`, so use the team’s existing virtualenv and installed dependencies.

`uvicorn app.main:app --reload`
Runs the API locally with auto-reload.

`python -m app.main`
Useful for import validation, but `uvicorn` is the normal development entrypoint.

`python scripts/ingest_pinecone.py`
Loads CSV-based RAG content into Pinecone; run only after `.env` is configured.

## Coding Style & Naming Conventions
Follow the existing Python style: 4-space indentation, snake_case for functions and modules, PascalCase for Pydantic and SQLAlchemy models, and uppercase for config fields like `OPENAI_API_KEY`. Keep route modules thin and move reusable logic into `app/services/` or `app/db/crud.py`. Prefer explicit response models and type hints on new endpoints.

## Testing Guidelines
There is no committed `tests/` directory yet. Add tests under `tests/` using `test_<module>.py` naming, and mirror the app structure where possible, such as `tests/api/test_health.py`. Prioritize coverage for auth, chat flows, and database CRUD behavior. At minimum, verify `GET /api/health/live` and `GET /api/health/ready` before merging backend changes.

## Commit & Pull Request Guidelines
Git history is sparse and inconsistent (`first commit`, `new change in readme`), so use short imperative commit messages with scope, such as `api: add session ownership check`. Keep pull requests focused. Include a summary of behavior changes, note any `.env` or schema impacts, link the issue when available, and attach request or response examples for API changes.

## Security & Configuration Tips
Secrets live in `.env` and are required by `app/config.py`; do not hardcode API keys or commit environment files. The app expects OpenAI, Pinecone, MongoDB, and JWT settings to be present even for local startup. Treat `mental_health.db` as local state, not source-controlled data.
