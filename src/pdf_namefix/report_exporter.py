"""Compatibility re-exports for infrastructure relocation."""

from pdf_namefix.infrastructure.report_exporter import (
    SUPPORTED_REPORT_FORMATS,
    render_json_report,
    render_markdown_report,
    render_report,
    report_to_dict,
    suggestion_to_dict,
    utc_now_iso,
    warning_to_dict,
    write_report,
)

__all__ = [
    "SUPPORTED_REPORT_FORMATS",
    "render_json_report",
    "render_markdown_report",
    "render_report",
    "report_to_dict",
    "suggestion_to_dict",
    "utc_now_iso",
    "warning_to_dict",
    "write_report",
]
