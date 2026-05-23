## CONTEXT
- Project conventions: PROJECT_CONVENTIONS.md
- API contracts: Section 18.12.1
- Existing: backend/api/auth.py, backend/core/dependencies.py
## MODULE: Health & Monitoring
### Goal
Expose public status diagnostics and an authenticated WebSocket testing pipe.
### Components to implement
- backend/api/health.py: Public endpoint GET /api/health. Validates Postgres
(SELECT 1), Binance Tool connectivity, and LLM providers. Encapsulates flaws
inside a success state with degraded node indicators (do not raise exceptions).
- backend/api/websocket.py: Authenticated pipe @websocket("/ws/test"). Inspects
incoming JWT parameter. Pushes connected state details, echoes client frames, and
cleanly cleans up resources during disconnect events.
- backend/main.py: Tie in Routers and hook the standard WebSocket handler loop.
- frontend/src/pages/Dashboard.tsx (Skeleton): Connect to health API on mount,
render component statuses, and place a 'Test WebSocket' button to verify real-time
packet exchange.
### Output format
Provide backend routers, revised main assembly file, and dashboard skeleton code.
Enforce strict socket connection closure on bad auth parameter headers.
