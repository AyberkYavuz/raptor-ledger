# 🦅 Raptor Ledger: AI Agent Trading Bot Platform

Raptor Ledger is a high-performance, modular, workflow-oriented AI crypto trading bot platform tailored for Binance. Built to deploy seamlessly on a local Mac Mini environment before rolling out via multi-container Docker environments, the platform pairs high-speed deterministic calculation modules with context-aware large language models (LLMs) orchestrated via LangGraph.

The system enforces production-grade guardrails, transactional data integrity, and strict separation between autonomous AI reasoning, deterministic computation, and financial market execution.

---

## 🚀 Core Tech Stack

- **Backend API Layer**: Python 3.11+, FastAPI (fully asynchronous execution matrix)
- **Agent Orchestration Framework**: LangGraph (state persistence via memory buffers and relational state adapters)
- **Database Layer**: PostgreSQL (PostgresApp engine, SQLAlchemy 2.0 Async engine with `asyncpg` dialect driver context)
- **Structured Telemetry Pipeline**: `structlog` (native JSON serialization streaming to stdout)
- **Frontend Presentation Layer**: React, TailwindCSS, TypeScript
- **Environment & Containment**: Multi-stage Docker & Docker-Compose

---

## 📚 Repository Blueprint & Architecture Roadmap

To maintain engineering transparency and demonstrate advanced software planning, all system specifications and AI prompt lifecycles are version-controlled alongside the application source code.

```text
raptor-ledger/
├── docs/                      # Technical specification & architecture blueprints
│   ├── Ai Agent Trading Bot Software Architecture Document V1.pdf
│   ├── PROJECT_CONVENTIONS.md # Coding rules, async invariants, logging standards
│   ├── database_schema.md    # Unified entity relationship & index specifications
│   └── error_codes.md        # Explicit domain failure exception map
├── prompts/                   # Prompt engineering lifecycle tracking
│   ├── README.md              # AI-Assisted Engineering methodology guidelines
│   └── module_0_foundation.md # Executed context prompt for skeleton initialization
├── backend/                   # Python application workspace
│   ├── core/                  # Core telemetry, configuration, and exception engines
│   ├── db/                    # Asynchronous session factory and connection pooler
│   ├── models/                # Structural SQLAlchemy physical model definitions
│   └── ...                    # Modular agents, tools, workflows, and API endpoints
└── frontend/                  # React dashboard workspace

### Documentation Directory Index
- **Coding Conventions & Guardrails**: Read [`docs/PROJECT_CONVENTIONS.md`](./docs/PROJECT_CONVENTIONS.md) to review the asynchronous constraints, structural logging setups, and test isolation principles.
- **Relational Storage Model Schema**: Read [`docs/database_schema.md`](./docs/database_schema.md) for the exact schema configurations, relationship maps, and index structures governing the database.
- **System Exception Domain Matrix**: Read [`docs/error_codes.md`](./docs/error_codes.md) to view the mapping of operational errors to specific HTTP status codes.

### AI-Assisted Prompt Engineering Logs
- **Prompt Engineering Directory**: Explore [`prompts/`](./prompts/) to understand how this platform utilizes high-context, deterministic, modular prompts to steer Large Language Models cleanly, maintaining full architectural consistency without code drift.

---

## 🛠️ Local Environment Fast-Start

The platform is designed to run natively on macOS using **PostgresApp** and **PyCharm** for rapid iterative development before compiling into isolated containerized services.

### 1. Initialize Database Core Specs
Ensure your local PostgreSQL engine is running on port `5432` with a valid catalog matching your local connection string in `env/backend-local.env`. 

Navigate into the backend repository, spin up your isolated virtual environment, and execute the physical metadata synchronization script:


# Synchronize structures and test asynchronous database integrity
python3 init_db.py

