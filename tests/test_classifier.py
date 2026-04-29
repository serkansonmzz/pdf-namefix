from pathlib import Path

from pdf_namefix.classifier import (
    classify_pdf_file,
    classify_pdf_files,
    keyword_matches,
    normalize_filename_for_matching,
)
from pdf_namefix.models import DocumentType, PdfFile


def make_pdf_file(name: str) -> PdfFile:
    return PdfFile(
        path=Path(name),
        source_root=Path("."),
        size_bytes=100,
    )


def test_normalize_filename_for_matching():
    normalized = normalize_filename_for_matching(Path("Clean-Architecture_Notes.v2.pdf"))

    assert normalized == "clean architecture notes v2"


def test_keyword_matches_whole_words():
    assert keyword_matches("clean architecture book", "book") is True


def test_keyword_does_not_match_inside_word():
    assert keyword_matches("bookkeeper contract", "book") is False


def test_classifies_invoice_from_english_keyword():
    classified = classify_pdf_file(make_pdf_file("stripe_invoice_2026.pdf"))

    assert classified.document_type == DocumentType.INVOICE
    assert classified.confidence == 0.9
    assert "invoice" in classified.reason


def test_classifies_invoice_from_turkish_keyword():
    classified = classify_pdf_file(make_pdf_file("turkcell_fatura_2026.pdf"))

    assert classified.document_type == DocumentType.INVOICE


def test_classifies_receipt_from_turkish_keyword():
    classified = classify_pdf_file(make_pdf_file("market_fiş.pdf"))

    assert classified.document_type == DocumentType.RECEIPT


def test_classifies_contract_from_turkish_keyword():
    classified = classify_pdf_file(make_pdf_file("kira_sözleşme.pdf"))

    assert classified.document_type == DocumentType.CONTRACT


def test_classifies_book():
    classified = classify_pdf_file(make_pdf_file("clean_architecture_book.pdf"))

    assert classified.document_type == DocumentType.BOOK


def test_classifies_course():
    classified = classify_pdf_file(make_pdf_file("rust_lifetimes_course.pdf"))

    assert classified.document_type == DocumentType.COURSE


def test_classifies_turkish_education_keyword_as_course():
    classified = classify_pdf_file(make_pdf_file("python_eğitim_materyali.pdf"))

    assert classified.document_type == DocumentType.COURSE


def test_classifies_lesson():
    classified = classify_pdf_file(make_pdf_file("english_lesson_01.pdf"))

    assert classified.document_type == DocumentType.LESSON


def test_classifies_notes():
    classified = classify_pdf_file(make_pdf_file("rust_lifetimes_notes.pdf"))

    assert classified.document_type == DocumentType.NOTES


def test_classifies_paper():
    classified = classify_pdf_file(make_pdf_file("transformer_research_paper.pdf"))

    assert classified.document_type == DocumentType.PAPER


def test_classifies_article():
    classified = classify_pdf_file(make_pdf_file("ai_agents_article.pdf"))

    assert classified.document_type == DocumentType.ARTICLE


def test_classifies_slides():
    classified = classify_pdf_file(make_pdf_file("agentic_workflows_slides.pdf"))

    assert classified.document_type == DocumentType.SLIDES


def test_classifies_manual():
    classified = classify_pdf_file(make_pdf_file("macbook_user_manual.pdf"))

    assert classified.document_type == DocumentType.MANUAL


def test_classifies_transcript():
    classified = classify_pdf_file(make_pdf_file("lex_fridman_transcript.pdf"))

    assert classified.document_type == DocumentType.TRANSCRIPT


def test_classifies_worksheet():
    classified = classify_pdf_file(make_pdf_file("english_exercises_worksheet.pdf"))

    assert classified.document_type == DocumentType.WORKSHEET


def test_classifies_guide():
    classified = classify_pdf_file(make_pdf_file("docker_deployment_guide.pdf"))

    assert classified.document_type == DocumentType.GUIDE


def test_classifies_cheatsheet():
    classified = classify_pdf_file(make_pdf_file("python_cheatsheet.pdf"))

    assert classified.document_type == DocumentType.CHEATSHEET


def test_classifies_generic_scan_as_document():
    classified = classify_pdf_file(make_pdf_file("scan_001.pdf"))

    assert classified.document_type == DocumentType.DOCUMENT
    assert classified.confidence == 0.3


def test_unknown_fallback():
    classified = classify_pdf_file(make_pdf_file("random_39281.pdf"))

    assert classified.document_type == DocumentType.UNKNOWN
    assert classified.confidence == 0.0


def test_classify_pdf_files_keeps_order():
    files = [
        make_pdf_file("one_invoice.pdf"),
        make_pdf_file("two_book.pdf"),
    ]

    classified = classify_pdf_files(files)

    assert [item.document_type for item in classified] == [
        DocumentType.INVOICE,
        DocumentType.BOOK,
    ]
