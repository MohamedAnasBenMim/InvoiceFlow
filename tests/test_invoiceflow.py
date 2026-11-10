from invoiceflow.benchmark import evaluate
from invoiceflow.extractor import BaselineExtractor, EnhancedExtractor
from invoiceflow.review import ReviewQueue
from invoiceflow.service import InvoiceService
from invoiceflow.validation import validate_invoice

COMPLETE = "Invoice: INV-1001\nSupplier: Atlas Office\nDate: 2026-10-01\nTotal: 480.50 EUR"


def test_extracts_complete_invoice() -> None:
    result = EnhancedExtractor().extract(COMPLETE)
    assert result.invoice_number == "INV-1001"
    assert result.supplier == "Atlas Office"
    assert result.total == 480.5
    assert result.currency == "EUR"
    assert result.uncertain_fields == []


def test_valid_invoice_is_straight_through() -> None:
    report = InvoiceService().process("invoice.txt", COMPLETE)
    assert report["route"] == "straight_through"
    assert report["validation"] == []


def test_missing_fields_route_to_human_review() -> None:
    service = InvoiceService()
    report = service.process("partial.txt", "Invoice: PART-1\nTotal: 10 EUR")
    assert report["route"] == "human_review"
    assert len(service.queue.list_pending()) == 1


def test_review_queue_can_resolve_item() -> None:
    queue = ReviewQueue()
    item = queue.enqueue("x", {}, ["missing"])
    queue.resolve(item.id)
    assert queue.list_pending() == []


def test_enhanced_extractor_beats_baseline() -> None:
    assert (
        evaluate(EnhancedExtractor(), 1)["field_accuracy"]
        > evaluate(BaselineExtractor(), 1)["field_accuracy"]
    )


def test_non_positive_total_is_rejected() -> None:
    extraction = EnhancedExtractor().extract(
        "Invoice: A-1\nSupplier: X\nDate: 2026-01-01\nTotal: 0 EUR"
    )
    assert any(issue.field == "total" for issue in validate_invoice(extraction))
