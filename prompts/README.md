# AI-Assisted Software Engineering Lifecycle

This directory contains the structured, high-context prompt engineering blueprints used to build **Raptor Ledger**. 

Rather than treating AI as a simple autocomplete tool, this project follows a **Modular Architecture-Driven Generation** methodology. Each prompt provides strict guardrails, design patterns, and context limits directly mapped from our `Software Architecture Document (SAD)`.

### Engineering Workflow
1. **Design**: Establish core architecture boundaries and write specifications (`docs/PROJECT_CONVENTIONS.md`).
2. **Context Delivery**: Feed localized constraints and database schemas into the LLM context.
3. **Execution**: Implement and test deterministically module by module, validating asynchronously in local environments before Dockerization.
