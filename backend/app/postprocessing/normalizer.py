"""Field normalization for dates, times, phones, emails, etc."""

import re
from typing import Optional, Dict, Any
import dateparser
from datetime import datetime


class FieldNormalizer:
    """Normalizes extracted field values to standard formats."""

    def normalize(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize all fields in extraction result.

        Args:
            extraction_result: Raw extraction result from LLM

        Returns:
            Normalized extraction result
        """
        fields = extraction_result.get('fields', {})

        # Normalize date fields
        for date_field in ['date', 'start_date', 'end_date']:
            if date_field in fields and fields[date_field]:
                value = fields[date_field].get('value')
                if value:
                    normalized = self._normalize_date(value)
                    if normalized != value:
                        fields[date_field]['value'] = normalized
                        fields[date_field]['normalized'] = True

        # Normalize time fields
        for time_field in ['time', 'start_time', 'end_time']:
            if time_field in fields and fields[time_field]:
                value = fields[time_field].get('value')
                if value:
                    normalized = self._normalize_time(value)
                    if normalized != value:
                        fields[time_field]['value'] = normalized
                        fields[time_field]['normalized'] = True

        # Normalize phone
        if 'contact_phone' in fields and fields['contact_phone']:
            value = fields['contact_phone'].get('value')
            if value:
                normalized = self._normalize_phone(value)
                if normalized != value:
                    fields['contact_phone']['value'] = normalized
                    fields['contact_phone']['normalized'] = True

        # Normalize email
        if 'contact_email' in fields and fields['contact_email']:
            value = fields['contact_email'].get('value')
            if value:
                normalized = self._normalize_email(value)
                if normalized != value:
                    fields['contact_email']['value'] = normalized
                    fields['contact_email']['normalized'] = True

        # Normalize URLs
        for url_field in ['website', 'registration_link']:
            if url_field in fields and fields[url_field]:
                value = fields[url_field].get('value')
                if value:
                    normalized = self._normalize_url(value)
                    if normalized != value:
                        fields[url_field]['value'] = normalized
                        fields[url_field]['normalized'] = True

        extraction_result['fields'] = fields
        return extraction_result

    def _normalize_date(self, date_str: str) -> str:
        """Parse various date formats to ISO 8601 (YYYY-MM-DD).

        Args:
            date_str: Date string in any format

        Returns:
            ISO 8601 formatted date or original string if parsing fails
        """
        try:
            parsed = dateparser.parse(
                date_str,
                settings={'PREFER_DATES_FROM': 'future'}
            )
            if parsed:
                return parsed.date().isoformat()
        except Exception:
            pass

        return date_str

    def _normalize_time(self, time_str: str) -> str:
        """Standardize time format to 24h (HH:MM or HH:MM-HH:MM).

        Args:
            time_str: Time string in any format

        Returns:
            24-hour formatted time or original string if parsing fails
        """
        # Handle ranges like "9am-5pm" or "09:00-17:00"
        if '-' in time_str or 'to' in time_str.lower():
            parts = re.split(r'\s*-\s*|\s+to\s+', time_str, flags=re.IGNORECASE)
            if len(parts) == 2:
                start = self._convert_to_24h(parts[0].strip())
                end = self._convert_to_24h(parts[1].strip())
                if start and end:
                    return f"{start}-{end}"

        # Single time
        converted = self._convert_to_24h(time_str)
        return converted if converted else time_str

    def _convert_to_24h(self, time_str: str) -> Optional[str]:
        """Convert time string to 24-hour format.

        Args:
            time_str: Time string

        Returns:
            24-hour formatted time (HH:MM) or None if parsing fails
        """
        # Pattern for HH:MM with optional am/pm
        pattern = r'(\d{1,2}):(\d{2})\s*([ap]m)?'
        match = re.search(pattern, time_str, re.IGNORECASE)

        if match:
            hour = int(match.group(1))
            minute = match.group(2)
            meridiem = match.group(3).lower() if match.group(3) else None

            if meridiem == 'pm' and hour < 12:
                hour += 12
            elif meridiem == 'am' and hour == 12:
                hour = 0

            return f"{hour:02d}:{minute}"

        # Pattern for just hour with am/pm
        pattern = r'(\d{1,2})\s*([ap]m)'
        match = re.search(pattern, time_str, re.IGNORECASE)

        if match:
            hour = int(match.group(1))
            meridiem = match.group(2).lower()

            if meridiem == 'pm' and hour < 12:
                hour += 12
            elif meridiem == 'am' and hour == 12:
                hour = 0

            return f"{hour:02d}:00"

        return None

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to standard format.

        Args:
            phone: Phone number string

        Returns:
            Formatted phone number (US format if applicable)
        """
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)

        # Format US numbers
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

        # Return original if not a standard US number
        return phone

    def _normalize_email(self, email: str) -> str:
        """Normalize email address.

        Args:
            email: Email address

        Returns:
            Lowercase, trimmed email
        """
        return email.lower().strip()

    def _normalize_url(self, url: str) -> str:
        """Normalize URL (ensure https:// prefix if missing).

        Args:
            url: URL string

        Returns:
            Normalized URL
        """
        url = url.strip()

        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            # Check if it looks like a URL (has domain-like structure)
            if '.' in url and not url.startswith('www.'):
                url = 'https://' + url
            elif url.startswith('www.'):
                url = 'https://' + url

        return url
