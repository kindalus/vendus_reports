"""Vendus Reports - Generate reports from Vendus API."""

__version__ = "1.0.0"
__author__ = "Kindalus"
__description__ = "A CLI tool to generate invoicing, receipts, SAFT, and tax analysis reports from Vendus API"

from .cli import (
    InvoicingReport,
    ReceiptReport,
    TaxReport,
    invoicing,
    receipts,
    tax_analysis,
    saft,
)

__all__ = [
    "InvoicingReport",
    "ReceiptReport", 
    "TaxReport",
    "invoicing",
    "receipts",
    "tax_analysis",
    "saft",
]