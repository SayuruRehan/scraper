"""
Deadline extraction and normalization utilities.
"""

import re
from datetime import datetime
from typing import Optional


# Common deadline patterns across scholarship pages
DEADLINE_PATTERNS = [
    # "Deadline: March 31, 2026" or "Application deadline: 31 March 2026" or "Deadline: 31 March 2026 (annual)"
    r"deadline[:\s]+(\d{1,2}\s+(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)[,\s]+\d{4})",
    r"deadline[:\s]+((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}[,\s]+\d{4})",
    
    # "Apply by: 31/03/2026" or "Closes: 03-31-2026" or "Close: 31 March 2026"
    r"(?:apply\s+by|closes?|closing\s+date)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
    r"(?:closes?)[:\s]+(\d{1,2}\s+(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)[,\s]+\d{4})",
    
    # "Application closes: March 31st 2026" or "Apply by: March 31st 2026"
    r"application\s+closes?[:\s]+((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?[,\s]+\d{4})",
    r"(?:apply\s+by)[:\s]+((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?[,\s]+\d{4})",
    
    # "Due date: March 31, 2026"
    r"due\s+date[:\s]+(\d{1,2}\s+(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)[,\s]+\d{4})",
    r"due\s+date[:\s]+((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}[,\s]+\d{4})",
    
    # ISO format "2026-03-31"
    r"\b(\d{4}-\d{2}-\d{2})\b",
]

MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def extract_deadline(text: str, source_patterns: list[str] | None = None) -> Optional[str]:
    """
    Extract application deadline from text using regex patterns.
    
    Args:
        text: Text to search for deadline information
        source_patterns: Optional list of source-specific regex patterns
    
    Returns:
        ISO date string (YYYY-MM-DD) or None if no deadline found
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Try source-specific patterns first
    patterns = (source_patterns or []) + DEADLINE_PATTERNS
    
    for pattern in patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            date_str = match.group(1).strip()
            normalized = _normalize_date(date_str)
            if normalized:
                return normalized
    
    return None


def _normalize_date(date_str: str) -> Optional[str]:
    """
    Normalize various date formats to ISO format (YYYY-MM-DD).
    
    Args:
        date_str: Date string in various formats
    
    Returns:
        ISO format date string or None if parsing fails
    """
    date_str = date_str.lower().strip()
    
    # Already ISO format
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            return None
    
    # "31 March 2026" or "March 31 2026"
    patterns = [
        (r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", lambda g: (int(g[0]), MONTH_MAP.get(g[1].lower(), 0), int(g[2]))),
        (r"([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?[,\s]+(\d{4})", lambda g: (int(g[1]), MONTH_MAP.get(g[0].lower(), 0), int(g[2]))),
    ]
    
    for pattern, extractor in patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                day, month, year = extractor(match.groups())
                if 1 <= month <= 12 and 1 <= day <= 31 and 2000 <= year <= 2100:
                    date_obj = datetime(year, month, day)
                    return date_obj.strftime("%Y-%m-%d")
            except (ValueError, KeyError, IndexError):
                continue
    
    # "31/03/2026" or "03/31/2026" or "31-03-2026"
    slash_match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", date_str)
    if slash_match:
        parts = [int(p) for p in slash_match.groups()]
        
        # Try DD/MM/YYYY first (more common internationally)
        try:
            if 1 <= parts[0] <= 31 and 1 <= parts[1] <= 12:
                date_obj = datetime(parts[2], parts[1], parts[0])
                return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            pass
        
        # Try MM/DD/YYYY
        try:
            if 1 <= parts[1] <= 31 and 1 <= parts[0] <= 12:
                date_obj = datetime(parts[2], parts[0], parts[1])
                return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            pass
    
    return None
