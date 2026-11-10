from __future__ import annotations

from dataclasses import asdict

from .extractor import EnhancedExtractor
from .review import ReviewQueue
from .validation import validate_invoice


class InvoiceService:
    def __init__(self, review_threshold: float = 0.8) -> None:
        self.extractor = EnhancedExtractor()
        self.queue = ReviewQueue()
        self.review_threshold = review_threshold

    def process(self, source_name: str, text: str) -> dict[str, object]:
        extraction = self.extractor.extract(text)
        issues = validate_invoice(extraction)
        reasons = [f"{issue.field}: {issue.message}" for issue in issues]
        reasons.extend(
            f"{field}: confidence below {self.review_threshold}"
            for field in extraction.uncertain_fields
        )
        review = (
            self.queue.enqueue(source_name, extraction.to_dict(), sorted(set(reasons)))
            if reasons
            else None
        )
        return {
            "source": source_name,
            "extraction": extraction.to_dict(),
            "validation": [asdict(issue) for issue in issues],
            "route": "human_review" if review else "straight_through",
            "review_id": review.id if review else None,
        }
