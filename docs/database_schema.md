# database_schema.md

## Database Architecture Overview
The database layer utilizes strict physical reference validation constraints, functional data indexing strategies, and transactional structural isolation models[cite: 412, 413].

```mermaid
erDiagram
    users ||--o{ trades : executes
    users ||--o{ agent_decisions : evaluates
    users ||--o{ llm_logs : profiles
    users ||--o{ portfolio_snapshots : snapshots

    users {
        uuid id PK
        string email UK
        string password_hash
        timestamp created_at
    }
    trades {
        uuid id PK
        uuid user_id FK
        string symbol
        string action
        float quantity
        float price
        float profit_loss
        string order_id
        timestamp timestamp
    }
    agent_decisions {
        uuid id PK
        uuid user_id FK
        string agent_name
        string decision
        float confidence
        text reason
        timestamp created_at
    }
    llm_logs {
        uuid id PK
        uuid user_id FK
        string model_name
        integer prompt_tokens
        integer completion_tokens
        float cost
        float latency
        string agent_name
        timestamp created_at
    }
    portfolio_snapshots {
        uuid id PK
        uuid user_id FK
        float balance
        float daily_pnl
        jsonb open_positions
        timestamp created_at
    }
