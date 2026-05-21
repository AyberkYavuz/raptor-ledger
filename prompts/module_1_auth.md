## CONTEXT
- Project conventions: see PROJECT_CONVENTIONS.md
- Database schema: see database_schema.md (User table already initialized)
- Error codes: see error_codes.md
- Existing: backend/db/base.py, backend/db/models.py, backend/core/logging.py,
backend/core/exceptions.py
## MODULE: Authentication
### Goal
Implement secure async user login, logout, and token authorization.
### Components to implement
#### Backend
- backend/api/auth.py: Endpoints:
- POST /api/auth/login: Expects email and password. Queries user, verifies hash
via passlib (bcrypt), mints JWT token via python-jose (24h validity, utilizing
JWT_SECRET_KEY setting). Throws 401 INVALID_CREDENTIALS on failure.
- POST /api/auth/logout: Discards token on client-side (stateless V1).
- backend/core/dependencies.py: Implement get_current_user security injection.
Extracts Bearer token from headers, decodes claims, fetches matching user model,
and intercepts invalid sessions.
- backend/core/config.py: Handle settings parsing for JWT keys and algorithm
schemes.
#### Frontend
- frontend/src/pages/Login.tsx: Create reactive interface using Tailwind CSS and
shadcn/ui. Captures inputs, posts login payload, stores token in localStorage, and
commands router push to /dashboard.
- frontend/src/services/api.ts: Configure base Axios instance equipped with
automatic request interceptors to append token signatures.
#### Tests
- backend/tests/test_auth.py: Test cryptographic hashing functions, token
extraction claims, dependency overrides, and valid/invalid credential login paths.
### Output format
Provide full production-ready code files with type annotations and concise
execution checks (e.g. pytest).
