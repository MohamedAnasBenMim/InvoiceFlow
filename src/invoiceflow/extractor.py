from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import ClassVar


@dataclass(slots=True)
class Extraction:
    invoice_number: str | None = None
    supplier: str | None = None
    issue_date: str | None = None
    total: float | None = None
    currency: str | None = None
    confidence: dict[str, float] = field(default_factory=dict)
    uncertain_fields: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class BaselineExtractor:
    def extract(self, text: str) -> Extraction:
        number = re.search(r"(?:invoice|inv)[\s#:-]*([A-Z0-9-]+)", text, re.IGNORECASE)
        total = re.search(r"total[\s:]*([0-9]+(?:[.,][0-9]{1,2})?)", text, re.IGNORECASE)
        return Extraction(
            invoice_number=number.group(1) if number else None,
            total=float(total.group(1).replace(",", ".")) if total else None,
        )


class EnhancedExtractor:
    FIELD_PATTERNS: ClassVar[dict[str, list[str]]] = {
        "invoice_number": [r"(?:invoice|inv)(?:\s+(?:number|no))?[\s#:-]*([A-Z0-9-]+)"],
        "supplier": [r"(?:supplier|vendor|from)[\s:]+([^\n]+)"],
        "issue_date": [
            r"(?:issue\s+date|date)[\s:]+(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})"
        ],
        "total": [r"(?:grand\s+total|amount\s+due|total)[^0-9]{0,12}([0-9]+(?:[.,][0-9]{1,2})?)"],
        "currency": [r"\b(EUR|USD|TND|GBP)\b", r"([$€£])"],
    }
    CURRENCY_SYMBOLS: ClassVar[dict[str, str]] = {"$": "USD", "€": "EUR", "£": "GBP"}

    def extract(self, text: str) -> Extraction:
        values: dict[str, object] = {}
        confidence: dict[str, float] = {}
        for field_name, patterns in self.FIELD_PATTERNS.items():
            match = next(
                (
                    match
                    for pattern in patterns
                    if (match := re.search(pattern, text, re.IGNORECASE))
                ),
                None,
            )
            if match:
                value: object = match.group(1).strip()
                if field_name == "total":
                    value = float(str(value).replace(",", "."))
                elif field_name == "currency":
                    value = self.CURRENCY_SYMBOLS.get(str(value), str(value).upper())
                elif field_name == "issue_date":
                    value = self._normalize_date(str(value))
                values[field_name] = value
                confidence[field_name] = 0.96 if field_name != "supplier" else 0.91
            else:
                values[field_name] = None
                confidence[field_name] = 0.0
        uncertain = [name for name, score in confidence.items() if score < 0.8]
        return Extraction(**values, confidence=confidence, uncertain_fields=uncertain)

    @staticmethod
    def _normalize_date(value: str) -> str:
        for pattern in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(value, pattern).date().isoformat()
            except ValueError:
                pass
        raise ValueError(f"unsupported date: {value}")
