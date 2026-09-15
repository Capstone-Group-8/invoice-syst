# Prepared Unit 5 Integration Changes

This package was prepared to accelerate the Alpha integration. Review before merging.

## Seth / interface-focused changes
- Added React/Vite frontend under `frontend/`.
- Frontend reads invoice and line-item data from FastAPI.
- Added environment-based frontend API URL.
- Corrected CORS configuration through `FRONTEND_ORIGINS`.

## Integration / CI cleanup
- Added `.github/workflows/ci.yml` for pytest + React build.
- Added `requirements.txt`, `.gitignore`, and `.env.example`.
- Default development DB is SQLite so the API can run without local MySQL; MySQL remains available through `DATABASE_URL`.
- Added `seed_demo.py` for a local interface demo.
- Repaired obvious schema/CRUD inconsistencies that blocked interface integration.
- Made unfinished pseudocode files syntactically valid placeholders.
- Repaired validation test class-name errors and the incorrect expected syntax string.
- Added conservative OCR field detection and a confidence-preserving helper. Full vendor parsing is still incomplete.

## Important
Do not claim peer review, Alpha completion, or a successful OCR-to-database workflow until the team actually verifies those items in GitHub/local testing.
