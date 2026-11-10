from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(slots=True)
class ReviewItem:
    id: str
    created_at: str
    source_name: str
    payload: dict[str, object]
    reasons: list[str]
    status: str = "pending"


class ReviewQueue:
    def __init__(self) -> None:
        self._items: dict[str, ReviewItem] = {}

    def enqueue(
        self, source_name: str, payload: dict[str, object], reasons: list[str]
    ) -> ReviewItem:
        item = ReviewItem(
            str(uuid4()), datetime.now(UTC).isoformat(), source_name, payload, reasons
        )
        self._items[item.id] = item
        return item

    def list_pending(self) -> list[dict[str, object]]:
        return [asdict(item) for item in self._items.values() if item.status == "pending"]

    def resolve(self, item_id: str) -> None:
        self._items[item_id].status = "resolved"
