"""Compatibility re-exports for infrastructure relocation."""

from pdf_namefix.infrastructure.ai_report_exporter import (
    ai_suggestion_to_dict,
    render_ai_json_report,
    render_ai_markdown_report,
    write_ai_report,
)

__all__ = [
    "ai_suggestion_to_dict",
    "render_ai_json_report",
    "render_ai_markdown_report",
    "write_ai_report",
]
