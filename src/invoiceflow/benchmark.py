from __future__ import annotations

import json
import time
from pathlib import Path

from .extractor import BaselineExtractor, EnhancedExtractor

DATASET = [
    (
        "Invoice: INV-1001\nSupplier: Atlas Office\nDate: 2026-10-01\nTotal: 480.50 EUR",
        {
            "invoice_number": "INV-1001",
            "supplier": "Atlas Office",
            "issue_date": "2026-10-01",
            "total": 480.5,
            "currency": "EUR",
        },
    ),
    (
        "INV NO #TUN-42\nVendor: Northwind SARL\nIssue Date: 02/10/2026\nAmount Due: 1200,00 TND",
        {
            "invoice_number": "TUN-42",
            "supplier": "Northwind SARL",
            "issue_date": "2026-10-02",
            "total": 1200.0,
            "currency": "TND",
        },
    ),
    (
        "Invoice US-77\nFrom: Contoso Inc\nDate: 2026/10/03\nGrand Total $99.95",
        {
            "invoice_number": "US-77",
            "supplier": "Contoso Inc",
            "issue_date": "2026-10-03",
            "total": 99.95,
            "currency": "USD",
        },
    ),
]


def evaluate(extractor: object, iterations: int = 200) -> dict[str, float]:
    correct = total = 0
    started = time.perf_counter()
    for _ in range(iterations):
        for text, expected in DATASET:
            result = extractor.extract(text)
            for field, value in expected.items():
                correct += getattr(result, field) == value
                total += 1
    elapsed = time.perf_counter() - started
    documents = iterations * len(DATASET)
    return {
        "field_accuracy": round(correct / total, 4),
        "mean_processing_ms": round(elapsed * 1000 / documents, 4),
        "estimated_cost_per_1k_usd": 0.0,
    }


def main() -> None:
    report = {"baseline": evaluate(BaselineExtractor()), "enhanced": evaluate(EnhancedExtractor())}
    path = Path("benchmarks/results.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
