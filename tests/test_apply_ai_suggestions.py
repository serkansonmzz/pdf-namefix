import json
from pathlib import Path

from pdf_namefix.services.apply_ai_suggestions import (
    apply_ai_suggestions_to_filename_suggestions,
    load_ai_suggestion_map,
)
from pdf_namefix.services.classifier import classify_pdf_file
from pdf_namefix.domain.models import DocumentType, PdfFile
from pdf_namefix.services.name_suggester import suggest_filenames


def make_pdf_file(name: str) -> PdfFile:
    return PdfFile(path=Path(name), source_root=Path("."), size_bytes=100)


def test_load_ai_suggestion_map(tmp_path: Path):
    path = tmp_path / "ai.json"
    source = tmp_path / "file.pdf"

    path.write_text(
        json.dumps(
            {
                "suggestions": [
                    {
                        "source_path": str(source),
                        "ai": {
                            "suggested_name": "unknown-date_file_book.pdf",
                            "document_type": "book",
                            "confidence": 0.9,
                            "should_apply": True,
                            "reason": "test",
                            "improvement": "test",
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    mapping = load_ai_suggestion_map(path)

    assert source in mapping


def test_apply_ai_suggestions_replaces_suggestion_when_confident():
    pdf_file = make_pdf_file("How-To-Lie-With-Statistics.pdf")
    classified = classify_pdf_file(pdf_file)
    suggestions = suggest_filenames([classified])

    ai_map = {
        pdf_file.path: {
            "suggested_name": "unknown-date_how_to_lie_with_statistics_darrell_huff_book.pdf",
            "document_type": "book",
            "confidence": 0.92,
            "should_apply": True,
            "reason": "Known public book.",
            "improvement": "Changed unknown to book.",
        }
    }

    updated = apply_ai_suggestions_to_filename_suggestions(
        suggestions=suggestions,
        ai_map=ai_map,
        min_confidence=0.8,
    )

    assert updated[0].suggested_name == "unknown-date_how_to_lie_with_statistics_darrell_huff_book.pdf"
    assert updated[0].classified_pdf_file.document_type == DocumentType.BOOK


def test_apply_ai_suggestions_ignores_low_confidence():
    pdf_file = make_pdf_file("How-To-Lie-With-Statistics.pdf")
    classified = classify_pdf_file(pdf_file)
    suggestions = suggest_filenames([classified])

    ai_map = {
        pdf_file.path: {
            "suggested_name": "better.pdf",
            "document_type": "book",
            "confidence": 0.4,
            "should_apply": True,
            "reason": "test",
            "improvement": "test",
        }
    }

    updated = apply_ai_suggestions_to_filename_suggestions(
        suggestions=suggestions,
        ai_map=ai_map,
        min_confidence=0.8,
    )

    assert updated[0].suggested_name == suggestions[0].suggested_name


def test_apply_ai_suggestions_accepts_profile_threshold_075():
    pdf_file = make_pdf_file("AI Destekli Yazilim Gelistirme Egitimi.pdf")
    classified = classify_pdf_file(pdf_file)
    suggestions = suggest_filenames([classified])

    ai_map = {
        pdf_file.path: {
            "suggested_name": "ai_destekli_yazilim_gelistirme_egitimi_study_material.pdf",
            "document_type": "study_material",
            "confidence": 0.75,
            "should_apply": True,
            "reason": "Training material.",
            "improvement": "Changed generic document to study_material.",
        }
    }

    updated = apply_ai_suggestions_to_filename_suggestions(
        suggestions=suggestions,
        ai_map=ai_map,
        min_confidence=0.70,
    )

    assert updated[0].suggested_name == "ai_destekli_yazilim_gelistirme_egitimi_study_material.pdf"
    assert updated[0].classified_pdf_file.document_type == DocumentType.STUDY_MATERIAL


def test_apply_ai_suggestions_still_skips_below_explicit_threshold():
    pdf_file = make_pdf_file("AI Destekli Yazilim Gelistirme Egitimi.pdf")
    classified = classify_pdf_file(pdf_file)
    suggestions = suggest_filenames([classified])

    ai_map = {
        pdf_file.path: {
            "suggested_name": "ai_destekli_yazilim_gelistirme_egitimi_study_material.pdf",
            "document_type": "study_material",
            "confidence": 0.75,
            "should_apply": True,
            "reason": "Training material.",
            "improvement": "Changed generic document to study_material.",
        }
    }

    updated = apply_ai_suggestions_to_filename_suggestions(
        suggestions=suggestions,
        ai_map=ai_map,
        min_confidence=0.80,
    )

    assert updated[0].suggested_name == suggestions[0].suggested_name
