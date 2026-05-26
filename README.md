# 🦅 Raptor Ledger: AI Agent Trading Bot Platform

Raptor Ledger is a high-performance, modular, workflow-oriented AI crypto trading bot platform tailored for Binance. Built to deploy seamlessly on a local Mac Mini environment before rolling out via multi-container Docker environments, the platform pairs high-speed deterministic calculation modules with context-aware large language models (LLMs) orchestrated via LangGraph.

The system enforces production-grade guardrails, transactional data integrity, and strict separation between autonomous AI reasoning, deterministic computation, and financial market execution.

---

## 🚀 Core Tech Stack

- **Backend API Layer**: Python 3.9+, FastAPI (fully asynchronous execution matrix supporting persistent TCP WebSocket protocol upgrades).
- **Agent Orchestration Framework**: LangGraph (state persistence via memory buffers and relational state adapters)
- **Database Layer**: PostgreSQL (SQLAlchemy 2.0 Async engine with `asyncpg` dialect driver context)
- **Security & Cryptography**: Native `bcrypt==4.0.1` hashing backend & asymmetric JWT claims token minting
- **Structured Telemetry Pipeline**: `structlog` (native JSON serialization streaming to stdout)
- **Frontend Presentation Layer**: React 18+, Vite, TypeScript, Tailwind CSS v4 (Sleek, Dark-Themed Command Cockpit equipped with an asynchronous real-time WebSocket state telemetry feed).
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
│   ├── module_0_foundation.md # Skeleton initialization context prompt
│   └── module_1_auth.md       # Executed authentication & frontend integration prompt
│   └── module_3_health_monitoring.md # Health Monitoring Module prompt
│   └── module_4_portfolio_trade_history.md # Portfolio & Trade History  Module prompt
├── env/                       # Environment configuration repository
│   └── backend-local.env      # Local database strings and cryptographic secrets
├── backend/                   # Python application workspace
│   ├── api/                   # FastAPI route definitions and controller layers
│   │   ├── auth.py            # Session management and access controllers
│   │   └── websocket.py       # Authenticated real-time telemetry pipe route
│   ├── core/                  # Telemetry, configurations, and security dependencies
│   ├── db/                    # Asynchronous session factory and connection pooler
│   ├── models/                # Structural SQLAlchemy physical model definitions
│   ├── schemas/               # Pydantic input/output validation models
│   ├── tests/                 # Pytest cryptographic boundary validation suites
│   ├── main.py                # Main PyCharm-executable server entrypoint
│   └── seed_module4.py        # Synchronize Module 4 tables and insert historical ledger metrics
│   └── seed_user.py           # Database verification profile seeder
└── frontend/                  # React Vite dashboard workspace
    ├── public/                # Static asset storage repository (Icons, manifests)
    ├── src/                   # React TypeScript core source application
    │   ├── pages/             # Layout screens (Login.tsx)
    │   ├── services/          # Axios Axios-instance network configurations (api.ts)
    │   ├── index.css          # Tailwind CSS v4 global styling sheet
    │   └── main.tsx           # Client entrypoint mounting application tree
    ├── vite.config.ts         # Vite bundler and Tailwind post-processor setup
    └── package.json           # Frontend dependency manifest
```

### Documentation Directory Index
- **Coding Conventions & Guardrails**: Read [`docs/PROJECT_CONVENTIONS.md`](./docs/PROJECT_CONVENTIONS.md) to review the asynchronous constraints, structural logging setups, and test isolation principles.
- **Relational Storage Model Schema**: Read [`docs/database_schema.md`](./docs/database_schema.md) for the exact schema configurations, relationship maps, and index structures governing the database.
- **System Exception Domain Matrix**: Read [`docs/error_codes.md`](./docs/error_codes.md) to view the mapping of operational errors to specific HTTP status codes.

### AI-Assisted Prompt Engineering Logs
- **Prompt Engineering Directory**: Explore [`prompts/`](./prompts/) to understand how this platform utilizes high-context, deterministic, modular prompts to steer Large Language Models cleanly, maintaining full architectural consistency without code drift.

---

## 🛠️ Local Environment Fast-Start
The platform is designed to run natively on macOS using PostgresApp and PyCharm for rapid iterative development before compiling into isolated containerized services.

### 1. Initialize and Seed the Database Core
Ensure your local PostgreSQL engine is running on port 5432 with a database matching your local connection string in env/backend-local.env.

Navigate into the backend repository, spin up your isolated virtual environment, and execute the physical metadata synchronization and seeding scripts:

```Bash
cd backend
source .venv/bin/activate
```

#### Synchronize database structures and models

```Bash
python init_db.py
```

####  Seed the default developer authentication account profile
```Bash
python seed_user.py
```

#### Synchronize Module 4 tables and insert historical ledger metrics
```Bash
python seed_module4.py
```

### 2. Execute Automated Tests
Run the asynchronous test suites:

```Bash
pytest backend/tests/test_auth.py -v -s
```

```Bash
pytest backend/tests/test_mock_infrastructure.py -v -s
```

```Bash
pytest backend/tests/test_portfolio_history.py -v -s
```

### 3. Launch the Backend API (via PyCharm or Terminal)
Run backend/main.py directly inside PyCharm to utilize the native debugger, or run it programmatically from your terminal:

```Bash
python main.py
```

The API engine will boot up under structlog supervision and begin listening on http://127.0.0.1:8000. You can verify its heartbeat state at /health.

### 4. Launch the Frontend Command UI
Open a secondary terminal window, install the compiled Node modules, and execute the Vite development compilation engine:

```Bash
cd frontend
npm install
npm run dev
```

The modern UI console will boot up on http://localhost:5173. Open the interface, enter your seeded credentials (ayberk@raptorledger.ai / securepassword123), and access the command cockpit.

