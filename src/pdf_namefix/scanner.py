"""Compatibility re-exports for services relocation."""

from pdf_namefix.services.scanner import (
    add_pdf_file_if_unique,
    is_pdf_file,
    iter_candidate_files,
    scan_pdf_files,
)

__all__ = [
    "add_pdf_file_if_unique",
    "is_pdf_file",
    "iter_candidate_files",
    "scan_pdf_files",
]
