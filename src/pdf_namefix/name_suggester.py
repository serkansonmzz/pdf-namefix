"""Compatibility re-exports for services relocation."""

from pdf_namefix.services.name_suggester import (
    DATE_PATTERNS,
    NOISE_WORDS,
    build_suffixed_filename,
    build_title_slug,
    clamp_filename,
    extract_date_from_name,
    has_any_collision,
    normalize_to_ascii,
    resolve_suggestion_collisions,
    slugify_filename_part,
    split_pdf_filename,
    strip_date_patterns,
    suggest_filename,
    suggest_filenames,
)

__all__ = [
    "DATE_PATTERNS",
    "NOISE_WORDS",
    "build_suffixed_filename",
    "build_title_slug",
    "clamp_filename",
    "extract_date_from_name",
    "has_any_collision",
    "normalize_to_ascii",
    "resolve_suggestion_collisions",
    "slugify_filename_part",
    "split_pdf_filename",
    "strip_date_patterns",
    "suggest_filename",
    "suggest_filenames",
]
