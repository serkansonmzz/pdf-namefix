"""Compatibility re-exports for services relocation."""

from pdf_namefix.services.pdf_inspector import (
    MAX_FIRST_PAGE_TEXT_CHARS,
    inspect_pdf_file,
    inspect_pdf_files,
    safe_str,
    truncate_text,
)

__all__ = [
    "MAX_FIRST_PAGE_TEXT_CHARS",
    "inspect_pdf_file",
    "inspect_pdf_files",
    "safe_str",
    "truncate_text",
]
