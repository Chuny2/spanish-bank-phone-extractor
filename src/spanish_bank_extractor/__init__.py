"""
Spanish Bank Phone Extractor

A modern application for extracting phone numbers from Spanish bank IBAN data.
Supports both CLI and GUI interfaces.
"""

__version__ = "1.0.0"
__author__ = "Spanish Bank Extractor Team"
__description__ = "Extract phone numbers from Spanish bank IBAN data"

from .core.extractor import SpanishBankExtractor
from .core.bank_registry import BankRegistry

__all__ = [
    "SpanishBankExtractor",
    "BankRegistry",
    "__version__",
    "__author__",
    "__description__"
] 