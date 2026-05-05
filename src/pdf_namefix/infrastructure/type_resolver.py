from pathlib import Path

from pdf_namefix.models import DocumentType


TYPE_SUFFIXES: list[tuple[str, DocumentType]] = [
    ("_language_learning.pdf", DocumentType.LANGUAGE_LEARNING),
    ("_study_material.pdf", DocumentType.STUDY_MATERIAL),
    ("_student_document.pdf", DocumentType.STUDENT_DOCUMENT),
    ("_whitepaper.pdf", DocumentType.WHITEPAPER),
    ("_cheatsheet.pdf", DocumentType.CHEATSHEET),
    ("_worksheet.pdf", DocumentType.WORKSHEET),
    ("_reference.pdf", DocumentType.REFERENCE),
    ("_payment.pdf", DocumentType.PAYMENT),
    ("_invoice.pdf", DocumentType.INVOICE),
    ("_receipt.pdf", DocumentType.RECEIPT),
    ("_contract.pdf", DocumentType.CONTRACT),
    ("_article.pdf", DocumentType.ARTICLE),
    ("_report.pdf", DocumentType.REPORT),
    ("_course.pdf", DocumentType.COURSE),
    ("_paper.pdf", DocumentType.PAPER),
    ("_guide.pdf", DocumentType.GUIDE),
    ("_manual.pdf", DocumentType.MANUAL),
    ("_exam.pdf", DocumentType.EXAM),
    ("_book.pdf", DocumentType.BOOK),
    ("_ebook.pdf", DocumentType.EBOOK),
    ("_document.pdf", DocumentType.DOCUMENT),
    ("_unknown.pdf", DocumentType.UNKNOWN),
]


def document_type_from_filename_suffix(path: Path) -> DocumentType | None:
    name = path.name.lower()

    for suffix, document_type in TYPE_SUFFIXES:
        if name.endswith(suffix):
            return document_type

    return None
