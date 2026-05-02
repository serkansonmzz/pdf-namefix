from pathlib import Path

from pdf_namefix.classifier import (
    classify_pdf_file,
    classify_pdf_files,
    keyword_matches,
    normalize_filename_for_matching,
)
from pdf_namefix.models import DocumentType, PdfFile, PdfInsights


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
    classified = classify_pdf_file(make_pdf_file("math_lesson_01.pdf"))

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
    classified = classify_pdf_file(make_pdf_file("math_exercises_worksheet.pdf"))

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


def test_classifies_lebenslauf_as_cv():
    classified = classify_pdf_file(make_pdf_file("Lebenslauf Durdu Eren.pdf"))

    assert classified.document_type == DocumentType.CV


def test_classifies_vize_form_as_visa():
    classified = classify_pdf_file(make_pdf_file("vize_form_ornegi.pdf"))

    assert classified.document_type == DocumentType.VISA


def test_classifies_ogrenci_belgesi_as_student_document():
    classified = classify_pdf_file(make_pdf_file("bilgisayar_programciligi_ogrenci_belgesi.pdf"))

    assert classified.document_type == DocumentType.STUDENT_DOCUMENT


def test_classifies_sinav_giris_belgesi_as_exam():
    classified = classify_pdf_file(make_pdf_file("Sinav Giris Belgesi-yeni-2026.pdf"))

    assert classified.document_type == DocumentType.EXAM


def test_classifies_enabiz_tahlilleri_as_medical():
    classified = classify_pdf_file(make_pdf_file("Enabiz-Tahlilleri.pdf"))

    assert classified.document_type == DocumentType.MEDICAL


def test_classifies_borc_detay_as_payment():
    classified = classify_pdf_file(make_pdf_file("Borc Detay Listesi_14-07-2025 13_48.pdf"))

    assert classified.document_type == DocumentType.PAYMENT


def test_classifies_oxford_dictionary_as_reference():
    classified = classify_pdf_file(make_pdf_file("Oxford_Collocations_Dictionary.pdf"))

    assert classified.document_type == DocumentType.REFERENCE


def test_classifies_grammar_book_as_language_learning():
    classified = classify_pdf_file(make_pdf_file("Essential Grammar in Use 4th Edition.pdf"))

    assert classified.document_type in {
        DocumentType.LANGUAGE_LEARNING,
        DocumentType.BOOK,
    }


def test_classifies_whitepaper():
    classified = classify_pdf_file(make_pdf_file("Newwhitepaper_Agents2.pdf"))

    assert classified.document_type == DocumentType.WHITEPAPER


def test_classifies_from_pdf_metadata_when_filename_is_weak():
    pdf_file = make_pdf_file("File0001.pdf")
    insights = PdfInsights(
        path=pdf_file.path,
        metadata_title="Essential Grammar in Use",
        metadata_subject="English grammar reference",
    )

    classified = classify_pdf_file(pdf_file, insights=insights)

    assert classified.document_type in {
        DocumentType.LANGUAGE_LEARNING,
        DocumentType.BOOK,
        DocumentType.REFERENCE,
    }
    assert classified.confidence == 0.75
    assert "metadata/text" in classified.reason


def test_classifies_from_first_page_text_when_filename_is_unknown():
    pdf_file = make_pdf_file("download.pdf")
    insights = PdfInsights(
        path=pdf_file.path,
        first_page_text="Luke's Podcast transcript advanced episode",
    )

    classified = classify_pdf_file(pdf_file, insights=insights)

    assert classified.document_type == DocumentType.TRANSCRIPT
    assert classified.confidence == 0.75
