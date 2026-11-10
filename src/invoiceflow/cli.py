import argparse
import json
from pathlib import Path

from .service import InvoiceService


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract and validate an invoice text file")
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    report = InvoiceService().process(args.document.name, args.document.read_text(encoding="utf-8"))
    print(json.dumps(report, indent=2))
