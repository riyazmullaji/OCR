"""Mock LLM adapter for testing without API calls."""

import asyncio
from typing import Dict, Any, List

from app.llm.base import LLMAdapter


class MockLLMAdapter(LLMAdapter):
    """Mock adapter that returns deterministic sample data for testing."""

    async def text_to_json(
        self,
        ocr_text: str,
        layout_blocks: List[Dict],
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """Return mock extraction from OCR text.

        Args:
            ocr_text: OCR extracted text (ignored in mock)
            layout_blocks: Text blocks (ignored in mock)
            timezone: Timezone (ignored in mock)

        Returns:
            Mock extraction result
        """
        # Simulate API latency
        await asyncio.sleep(0.5)

        return {
            "fields": {
                "event_name": {
                    "value": "Mock Tech Conference 2026",
                    "confidence": 0.95,
                    "source": "line 1"
                },
                "date": {
                    "value": "2026-03-15",
                    "confidence": 0.90,
                    "source": "line 2"
                },
                "time": {
                    "value": "09:00-17:00",
                    "confidence": 0.85,
                    "source": "line 3"
                },
                "venue_name": {
                    "value": "Convention Center",
                    "confidence": 0.92,
                    "source": "line 4"
                },
                "venue_address": {
                    "value": "123 Main Street, San Francisco, CA 94105",
                    "confidence": 0.88,
                    "source": "line 5"
                },
                "description": {
                    "value": "Annual technology conference featuring the latest in AI and ML",
                    "confidence": 0.80,
                    "source": "lines 6-8"
                },
                "organizer": {
                    "value": "Tech Org Inc",
                    "confidence": 0.75,
                    "source": "line 9"
                },
                "contact_email": {
                    "value": "info@mocktech.com",
                    "confidence": 0.90,
                    "source": "line 10"
                },
                "contact_phone": {
                    "value": "(555) 123-4567",
                    "confidence": 0.85,
                    "source": "line 11"
                },
                "ticket_price": {
                    "value": "$50",
                    "confidence": 0.80,
                    "source": "line 12"
                },
                "website": {
                    "value": "https://mocktech.com",
                    "confidence": 0.95,
                    "source": "line 13"
                }
            },
            "extra": [
                {
                    "key": "wifi_available",
                    "value": "Yes",
                    "confidence": 0.70,
                    "source": "line 14"
                },
                {
                    "key": "refreshments",
                    "value": "Coffee and snacks provided",
                    "confidence": 0.65,
                    "source": "line 15"
                }
            ]
        }

    async def image_to_json(
        self,
        image_bytes: bytes,
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """Return mock extraction from image.

        Args:
            image_bytes: Image data (ignored in mock)
            timezone: Timezone (ignored in mock)

        Returns:
            Mock extraction result (same as text_to_json)
        """
        # Simulate API latency (vision calls are typically slower)
        await asyncio.sleep(1.0)

        # Return same mock data as text_to_json
        return await self.text_to_json("", [], timezone)
