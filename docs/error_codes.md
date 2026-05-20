| Error Code Namespace | System Exception Intent | Target HTTP Status |
| :--- | :--- | :--- |
| `INVALID_REQUEST` | Incoming telemetry parsing payload breaks structural schemas. | 400 Bad Request |
| `INVALID_TRADING_CONFIGURATION` | Specified target token list parameters fall outside configuration bounds[cite: 645]. | 400 Bad Request |
| `UNAUTHORIZED` | Security parameters missing or verification keys rejected. | 401 Unauthorized |
| `INVALID_CREDENTIALS` | Cryptographic signature checks or user password validation matching fails. | 401 Unauthorized |
| `TRADING_ALREADY_ACTIVE` | State update requested on engine while loop routines are executionally active. | 409 Conflict |
| `INSUFFICIENT_BALANCE` | Account margins fall below parameters needed to safely cover trading sizes. | 422 Unprocessable Entity |
| `BINANCE_API_ERROR` | Remote infrastructure timeouts or market data retrieval failures[cite: 676, 712]. | 502 Bad Gateway |
| `LLM_QUOTA_EXCEEDED` | Upstream model gateway throttles execution requests[cite: 712]. | 502 Bad Gateway |
| `BACKTEST_DATA_MISSING` | Time-series data blocks missing from cache layers during operational requests. | 500 Internal Server Error |
