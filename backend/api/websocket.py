# backend/api/websocket.py
import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt

from backend.core.config import settings

logger = structlog.get_logger("raptor_ledger.api.websocket")
router = APIRouter(tags=["WebSockets"])

logger.info("websocket.py begins")


@router.websocket("/ws/test")
async def websocket_test_endpoint(
    websocket: WebSocket,
    token: str = Query(None)
):
    """Authenticated real-time pipe enforcing strict closure on invalid tokens."""
    await websocket.accept()
    logger.info("Incoming WebSocket connection initialized. Parsing authentication token context...")

    if not token:
        logger.warn("WebSocket handshake rejected: Token query parameter missing.")
        await websocket.close(code=4001, reason="Authentication token parameter missing.")
        return

    try:
        # Validate the token using credentials parsed via settings matrix
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_email = payload.get("sub")
        if user_email is None:
            raise JWTError("Subject identity missing in claims.")
    except JWTError as e:
        logger.warn("Cryptographic verification trace invalid or expired for WebSocket.", error=str(e))
        await websocket.close(code=4002, reason="Token signature holding expired or corrupt matrix.")
        return

    logger.info("WebSocket connection fully authenticated", user=user_email)
    await websocket.send_json({
        "event": "connected",
        "details": f"Secure testing pipeline established for {user_email}."
    })

    try:
        while True:
            # Simple echoing system loop
            client_data = await websocket.receive_text()
            logger.debug("Received text frame context", data=client_data)
            await websocket.send_json({
                "event": "echo",
                "payload": client_data
            })
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected normally.", user=user_email)
    except Exception as e:
        logger.error("Unexpected error tracking active socket lifecycle", error=str(e))
