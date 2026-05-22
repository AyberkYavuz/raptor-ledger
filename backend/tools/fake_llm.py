# backend/tools/fake_llm.py
"""
FakeLLM – deterministic LLM response simulator for offline workflow testing.
No API calls, no costs. Parses prompt keywords to return structured JSON.
"""

import asyncio
import json
from typing import Any, Dict, Optional

import structlog
from structlog.stdlib import BoundLogger

logger: BoundLogger = structlog.get_logger(__name__)

logger.info("fake_llm.py begins")


class FakeLLM:
    """
    Simulates an LLM API (e.g., OpenAI) with keyword-triggered responses.
    Can simulate timeouts or malformed JSON for error testing.
    """

    def __init__(self):
        # Error simulation flags (set from tests or config)
        self.simulate_timeout: bool = False
        self.simulate_malformed_json: bool = False
        self.simulate_low_confidence: bool = False
        self.latency_seconds: float = 0.0  # artificial delay

    async def generate(self, prompt: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a mock response based on keywords in the prompt.

        Args:
            prompt: Input prompt string.
            schema: Optional expected JSON schema (ignored in mock).

        Returns:
            Structured mock response as dict.

        Raises:
            TimeoutError: If simulate_timeout is True.
            json.JSONDecodeError: If simulate_malformed_json is True.
        """
        if self.latency_seconds > 0:
            await asyncio.sleep(self.latency_seconds)

        if self.simulate_timeout:
            logger.error("FakeLLM simulated timeout")
            raise TimeoutError("Request timed out")

        if self.simulate_malformed_json:
            # Return invalid JSON string (will cause decoding error)
            return "This is not JSON"

        prompt_lower = prompt.lower()

        # Sentiment analysis response
        if "sentiment" in prompt_lower:
            if self.simulate_low_confidence:
                return {
                    "market_sentiment": "neutral",
                    "confidence": 0.45,
                    "reason": "Mock low confidence due to conflicting indicators."
                }
            return {
                "market_sentiment": "bullish",
                "confidence": 0.78,
                "reason": "Positive ETF inflow signals and strong on-chain activity (mock)."
            }

        # Trade decision response
        if "decision" in prompt_lower:
            if self.simulate_low_confidence:
                return {
                    "decision": "HOLD",
                    "confidence": 0.51,
                    "reason": "Insufficient signal strength; waiting for confirmation."
                }
            return {
                "decision": "BUY",
                "confidence": 0.82,
                "reason": "Strong momentum with bullish sentiment and volume spike."
            }

        # Generic fallback
        return {
            "output": "Mock response from FakeLLM",
            "confidence": 0.5,
            "reason": "No specific keyword matched."
        }

    async def generate_with_schema(self, prompt: str, schema: Dict) -> Dict[str, Any]:
        """Alias for generate() – ensures schema-compatible output."""
        return await self.generate(prompt, schema)
