"""Compatibility re-exports for infrastructure relocation."""

from pdf_namefix.infrastructure.type_resolver import (
    TYPE_SUFFIXES,
    document_type_from_filename_suffix,
)

__all__ = [
    "TYPE_SUFFIXES",
    "document_type_from_filename_suffix",
]
