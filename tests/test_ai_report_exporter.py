from pathlib import Path

from pdf_namefix.ai_report_exporter import render_ai_markdown_report, render_ai_json_report
from pdf_namefix.models import AiNamingSuggestion, DocumentType


def make_suggestion():
    return AiNamingSuggestion(
        source_path=Path("How-To-Lie-With-Statistics.pdf"),
        source_name="How-To-Lie-With-Statistics.pdf",
        current_suggested_name="unknown-date_how_to_lie_with_statistics_unknown.pdf",
        current_document_type=DocumentType.UNKNOWN,
        current_confidence=0.0,
        ai_suggested_name="unknown-date_how_to_lie_with_statistics_darrell_huff_book.pdf",
        ai_document_type=DocumentType.BOOK,
        semantic_type="public_book",
        confidence=0.92,
        reason="Known public book title.",
        improvement="Changed type from unknown to book and added author.",
        should_apply=True,
    )


def test_render_ai_markdown_report():
    content = render_ai_markdown_report([make_suggestion()], model="test-model")

    assert "# pdf-namefix AI Suggestions" in content
    assert "How-To-Lie-With-Statistics.pdf" in content
    assert "public_book" in content
    assert "darrell_huff" in content


def test_render_ai_json_report():
    content = render_ai_json_report([make_suggestion()], model="test-model")

    assert '"source_name": "How-To-Lie-With-Statistics.pdf"' in content
    assert '"semantic_type": "public_book"' in content
