"""Compatibility re-exports for the phase-3 domain split.

Prefer importing from:
- pdf_namefix.domain.models
- pdf_namefix.domain.ai_models
"""

from pdf_namefix.domain.ai_models import AiNamingInput, AiNamingSuggestion
from pdf_namefix.domain.models import (
    ClassifiedPdfFile,
    DocumentType,
    FilenameSuggestion,
    OrganizePlan,
    OrganizePlanItem,
    OrganizeResult,
    OrganizeResultItem,
    PdfFile,
    PdfInsights,
    RenamePlan,
    RenamePlanItem,
    RenameResult,
    RenameResultItem,
    ScanResult,
    ScanWarning,
)

__all__ = [
    "AiNamingInput",
    "AiNamingSuggestion",
    "ClassifiedPdfFile",
    "DocumentType",
    "FilenameSuggestion",
    "OrganizePlan",
    "OrganizePlanItem",
    "OrganizeResult",
    "OrganizeResultItem",
    "PdfFile",
    "PdfInsights",
    "RenamePlan",
    "RenamePlanItem",
    "RenameResult",
    "RenameResultItem",
    "ScanResult",
    "ScanWarning",
]
