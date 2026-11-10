from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .extractor import Extraction


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    field: str
    message: str
    severity: str


def validate_invoice(extraction: Extraction) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for field_name in ("invoice_number", "supplier", "issue_date", "total", "currency"):
        if getattr(extraction, field_name) in (None, ""):
            issues.append(ValidationIssue(field_name, "required field is missing", "error"))
    if extraction.total is not None and extraction.total <= 0:
        issues.append(ValidationIssue("total", "total must be positive", "error"))
    if extraction.issue_date and date.fromisoformat(extraction.issue_date) > date.today():
        issues.append(ValidationIssue("issue_date", "invoice date is in the future", "warning"))
    return issues
