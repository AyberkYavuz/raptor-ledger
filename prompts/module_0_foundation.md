## CONTEXT
We are building an AI Agent Trading Bot (crypto, Binance, Mac Mini, FastAPI,
React, PostgreSQL, LangGraph). No existing code yet.
## MODULE: Foundation & Full Database Schema
### Goal
Create the project skeleton, Docker environment, all shared configuration files,
and the complete database schema (all tables defined at once). This prevents
Alembic migration conflicts later.
### Components to generate
#### 1. Project folder structure
Create the following directories and placeholder __init__.py files:
backend/
api/, agents/, workflows/, tools/, services/, db/, models/, schemas/, core/,
tests/
frontend/
src/
components/, pages/, hooks/, services/, utils/
public/
docker/
postgres/
#### 2. docker-compose.yml
- Services: postgres (15), backend (FastAPI, build from ./backend), frontend
(React, build from ./frontend)
- Use volumes for persistent postgres data; expose ports: 5432 (postgres), 8000
(backend), 3000 (frontend)
- Setup environment variables for database credentials.
#### 3. .env.example
List all environment variables with placeholder values:
- DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/tradingbot
- JWT_SECRET_KEY=change_me
- BINANCE_API_KEY=, BINANCE_API_SECRET=
- BINANCE_TESTNET_API_KEY=, BINANCE_TESTNET_SECRET_KEY=
- OPENAI_API_KEY=, OPENROUTER_API_KEY=
- TRADING_ENABLED=false, MAX_DAILY_LOSS=20, LOG_LEVEL=INFO
- USE_MOCK_BINANCE=true, USE_FAKE_LLM=true, LIVE_TRADING_ENABLED=false
- MAX_POSITION_SIZE_USD=50, MAX_DAILY_TRADES=10
#### 4. PROJECT_CONVENTIONS.md
Write a markdown file specifying:
- Logging: Use structlog, JSON format, bind request_id, module name, timestamp.
- Error handling: Define raise_http_exception(status_code, error_code, message)
helper.
- Async patterns: All FastAPI endpoints and database calls must be async. Use
async_sessionmaker.
- Response format: Enforce standard shape: {success: bool, message: str, data:
any, error_code: str}
- Testing: Use pytest with asyncio. Mock external networks.
- Checkpointing: Enforce LangGraph state persistence using memory buffers or
Postgres adapters.
#### 5. database_schema.md
Define complete SQLAlchemy models with indexes and explicit foreign keys:
- User: id (UUID PK), email (String unique index), password_hash (String),
created_at (DateTime)
- Trade: id (UUID PK), user_id (FK), symbol, action (BUY/SELL), quantity, price,
profit_loss (nullable), timestamp, order_id
- AgentDecision: id (UUID PK), user_id (FK), agent_name, decision (BUY/SELL/HOLD),
confidence (Float), reason (Text), created_at
- LLMLog: id (UUID PK), user_id (FK), model_name, prompt_tokens,
completion_tokens, cost (Float), latency (Float), agent_name, created_at
- PortfolioSnapshot: id (UUID PK), user_id (FK), balance (Float), daily_pnl
(Float), open_positions (JSONB), created_at
#### 6. error_codes.md
Map core operational failures (INVALID_REQUEST, UNAUTHORIZED,
TRADING_ALREADY_ACTIVE, INSUFFICIENT_BALANCE, BINANCE_API_ERROR,
LLM_QUOTA_EXCEEDED, INVALID_CREDENTIALS, INVALID_TRADING_CONFIGURATION,
BACKTEST_DATA_MISSING) to HTTP statuses.
#### 7. Base Core Files
- backend/db/base.py: Create async engine, Base declarative mapping,
AsyncSessionLocal, and get_db() dependency.
- backend/core/logging.py: Configure JSON structlog pipeline.
- backend/core/exceptions.py: Implement HTTPExceptionWithCode and
raise_http_exception helper.
### Output format
Provide each file's full content in separate markdown code blocks with the file
path clearly commented. Include quick docker-compose up setup guidance.
