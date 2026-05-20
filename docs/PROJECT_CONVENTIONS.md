# PROJECT_CONVENTIONS.md

## 1. Asynchronous Design Strategy
- **Core Principle**: Blockages inside asynchronous runtimes collapse throughput. All I/O operations must use native Python `async/await` syntax.
- **Database Rules**: Threaded drivers like `psycopg2` are explicitly banned. Database interactions must resolve through `SQLAlchemy` using the `asyncpg` dialect driver contextually inside an `AsyncSession` block.
- **Network Requests**: `requests` or any synchronous API framework is strictly prohibited. Network boundaries must be bridged with `httpx.AsyncClient` or `aiohttp`.

## 2. Structured Ingestion Logging Pipeline
- All logging must use `structlog` formatted natively to output raw serialized JSON chunks to stdout.
- Trace contexts must pass through interceptors to inject fields dynamically into every log execution context:
  - `request_id`: Extracted from internal request header middleware.
  - `module_name`: The context locator namespace string.
  - `timestamp`: Serialized standard ISO 8601 formatting.

## 3. Strict Boundary Error Protocol
- Direct unchecked error bubbles down to root application logic must be caught via custom exception handlers to guarantee operational privacy.
- Standard response formatting requires a hard structural shape variant across errors:
  ```json
  {
    "success": false,
    "message": "Human readable context describing localized failure.",
    "data": null,
    "error_code": "SPECIFIC_UPPERCASE_ERROR_ENUM_STRING"
  }
