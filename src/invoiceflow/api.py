from fastapi import FastAPI
from pydantic import BaseModel

from .service import InvoiceService

app = FastAPI(title="InvoiceFlow", version="1.0.0")
service = InvoiceService()


class InvoiceText(BaseModel):
    source_name: str
    text: str


@app.post("/v1/invoices/process")
def process_invoice(invoice: InvoiceText) -> dict[str, object]:
    return service.process(invoice.source_name, invoice.text)


@app.get("/v1/reviews")
def reviews() -> list[dict[str, object]]:
    return service.queue.list_pending()
