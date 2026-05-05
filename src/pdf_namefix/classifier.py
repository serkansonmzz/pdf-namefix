"""Compatibility re-exports for services relocation."""

from pdf_namefix.services.classifier import (
    KEYWORD_RULES,
    classify_pdf_file,
    classify_pdf_files,
    keyword_matches,
    normalize_filename_for_matching,
    normalize_text_for_matching,
)

__all__ = [
    "KEYWORD_RULES",
    "classify_pdf_file",
    "classify_pdf_files",
    "keyword_matches",
    "normalize_filename_for_matching",
    "normalize_text_for_matching",
]
