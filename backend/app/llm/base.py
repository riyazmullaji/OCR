"""Abstract base class for LLM adapters."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class LLMAdapter(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def text_to_json(
        self,
        ocr_text: str,
        layout_blocks: List[Dict],
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """Extract structured JSON from OCR text.

        Args:
            ocr_text: Full OCR extracted text
            layout_blocks: List of text blocks with bounding boxes
            timezone: Timezone for date/time interpretation

        Returns:
            Dictionary with 'fields' and 'extra' keys containing extracted data
        """
        pass

    @abstractmethod
    async def image_to_json(
        self,
        image_bytes: bytes,
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """Extract structured JSON directly from image using vision capabilities.

        Args:
            image_bytes: Raw image bytes
            timezone: Timezone for date/time interpretation

        Returns:
            Dictionary with 'fields' and 'extra' keys containing extracted data
        """
        pass

    def _build_extraction_prompt(self, context: str = "", timezone: str = "UTC") -> str:
        """Build prompt for event data extraction.

        Args:
            context: Additional context (e.g., OCR text)
            timezone: Timezone for interpretation

        Returns:
            Formatted prompt string
        """
        return f"""Extract event information from the provided content and return ONLY a JSON object with this structure:

{{
  "fields": {{
    "event_name": {{"value": "Conference Title", "confidence": 0.95, "source": "line 1"}},
    "date": {{"value": "2026-03-15", "confidence": 0.90, "source": "line 2"}},
    "time": {{"value": "09:00-17:00", "confidence": 0.85, "source": "line 3"}},
    "venue_name": {{"value": "Convention Center", "confidence": 0.92, "source": "line 4"}},
    "venue_address": {{"value": "123 Main St, City, State", "confidence": 0.88, "source": "line 5"}},
    "description": {{"value": "Event description", "confidence": 0.80, "source": "lines 6-8"}},
    "organizer": {{"value": "Organizing Entity", "confidence": 0.75, "source": "line 10"}},
    "contact_email": {{"value": "info@event.com", "confidence": 0.90, "source": "line 11"}},
    "contact_phone": {{"value": "(555) 123-4567", "confidence": 0.85, "source": "line 12"}},
    "ticket_price": {{"value": "$50", "confidence": 0.80, "source": "line 13"}},
    "website": {{"value": "https://event.com", "confidence": 0.95, "source": "line 14"}},
    "registration_link": {{"value": "https://event.com/register", "confidence": 0.90, "source": "line 15"}}
  }},
  "extra": [
    {{"key": "dress_code", "value": "Business casual", "confidence": 0.70, "source": "line 16"}},
    {{"key": "parking_info", "value": "Free parking", "confidence": 0.65, "source": "line 17"}}
  ]
}}

**IMPORTANT RULES:**
1. Use timezone: {timezone} for date/time interpretation
2. Only include fields that are actually present (use null for missing fields or omit them)
3. Confidence: 0.0-1.0 based on text clarity and certainty
4. Source: reference to where the information was found (e.g., "line 1", "top banner", "bottom left")
5. Core fields belong in "fields" object: event_name, date, time, venue_name, venue_address, description, organizer, contact_email, contact_phone, ticket_price, website, registration_link
6. Any additional non-core information goes in "extra" array with key-value pairs
7. Return ONLY valid JSON - no markdown code blocks, no explanations, no additional text
8. Use ISO 8601 format for dates (YYYY-MM-DD) when possible
9. Use 24-hour format for times (HH:MM or HH:MM-HH:MM) when possible

{context}

Remember: Return ONLY the JSON object, nothing else."""
