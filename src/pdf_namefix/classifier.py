import re
from pathlib import Path

from pdf_namefix.models import ClassifiedPdfFile, DocumentType, PdfFile


KEYWORD_RULES: list[tuple[DocumentType, tuple[str, ...]]] = [
    (
        DocumentType.VISA,
        (
            "vize",
            "visa",
            "tlscontact",
        ),
    ),
    (
        DocumentType.CV,
        (
            "cv",
            "resume",
            "lebenslauf",
            "curriculum vitae",
        ),
    ),
    (
        DocumentType.STUDENT_DOCUMENT,
        (
            "ogrenci",
            "öğrenci",
            "mezun",
            "ogrenci belgesi",
            "öğrenci belgesi",
            "student certificate",
        ),
    ),
    (
        DocumentType.EXAM,
        (
            "sinav",
            "sınav",
            "sınav giriş",
            "sinav giris",
            "exam",
            "vize sinav",
            "ara sinav",
            "final sinav",
            "ielts",
            "telc",
            "a1 a2",
            "a2 b1",
            "c2",
        ),
    ),
    (
        DocumentType.MEDICAL,
        (
            "enabiz",
            "e-nabiz",
            "tahlil",
            "tahlilleri",
            "medical",
            "saglik",
            "sağlık",
            "kapsul",
            "kapsül",
            "ilac",
            "ilaç",
        ),
    ),
    (
        DocumentType.PAYMENT,
        (
            "tahsilat",
            "odeme",
            "ödeme",
            "odemeplani",
            "ödemeplani",
            "borc",
            "borç",
        ),
    ),
    (
        DocumentType.REFERENCE,
        (
            "dictionary",
            "collocations",
            "wortliste",
            "reference",
            "quick reference",
        ),
    ),
    (
        DocumentType.LANGUAGE_LEARNING,
        (
            "english",
            "german",
            "italian",
            "grammar",
            "vocabulary",
            "speaking",
            "listening",
            "ielts",
            "telc",
            "reader at work",
            "learn english",
            "short stories in english",
            "short stories in german",
            "short stories in italian",
            "fluent forever",
        ),
    ),
    (
        DocumentType.STUDY_MATERIAL,
        (
            "study plan",
            "calisma kagidi",
            "çalışma kağıdı",
            "haftalik program",
            "haftalık program",
            "unite",
            "ünite",
            "ders",
            "auzef",
            "matematik",
            "iktisat",
            "isletme",
            "işletme",
            "yonetim bilisim",
            "yönetim bilişim",
        ),
    ),
    (
        DocumentType.NOVEL,
        (
            "dune",
            "herman hesse",
            "journey to the east",
            "nasreddin hoca",
            "pardayanlar",
            "short stories",
        ),
    ),
    (
        DocumentType.WHITEPAPER,
        (
            "whitepaper",
            "newwhitepaper",
        ),
    ),
    (
        DocumentType.INVOICE,
        (
            "invoice",
            "fatura",
            "bill",
            "billing",
        ),
    ),
    (
        DocumentType.RECEIPT,
        (
            "receipt",
            "makbuz",
            "fis",
            "fiş",
            "payment-receipt",
        ),
    ),
    (
        DocumentType.CONTRACT,
        (
            "contract",
            "agreement",
            "sozlesme",
            "sözleşme",
        ),
    ),
    (
        DocumentType.REPORT,
        (
            "report",
            "rapor",
        ),
    ),
    (
        DocumentType.STATEMENT,
        (
            "statement",
            "hesap-ozeti",
            "hesap_ozeti",
            "hesap özeti",
            "bank-statement",
        ),
    ),
    (
        DocumentType.TAX,
        (
            "tax",
            "vergi",
        ),
    ),
    (
        DocumentType.OFFER,
        (
            "offer",
            "quotation",
            "quote",
            "teklif",
        ),
    ),
    (
        DocumentType.APPLICATION,
        (
            "application",
            "basvuru",
            "başvuru",
        ),
    ),
    (
        DocumentType.EBOOK,
        (
            "ebook",
            "e-book",
        ),
    ),
    (
        DocumentType.BOOK,
        (
            "book",
            "kitap",
            "e-kitap",
            "ekitap",
            "edition",
            "pdf kitap",
            "essential grammar in use",
            "advanced grammar in use",
            "power of now",
            "building applications",
        ),
    ),
    (
        DocumentType.COURSE,
        (
            "course",
            "kurs",
            "training",
            "egitim",
            "eğitim",
        ),
    ),
    (
        DocumentType.LESSON,
        (
            "lesson",
            "ders",
            "lecture",
        ),
    ),
    (
        DocumentType.NOTES,
        (
            "notes",
            "note",
            "notlar",
        ),
    ),
    (
        DocumentType.PAPER,
        (
            "paper",
            "academic-paper",
            "research",
            "makale",
            "article-paper",
        ),
    ),
    (
        DocumentType.ARTICLE,
        (
            "article",
            "yazi",
            "yazı",
        ),
    ),
    (
        DocumentType.SLIDES,
        (
            "slides",
            "slide",
            "presentation",
            "deck",
            "sunum",
            "pptx",
            "figjam",
        ),
    ),
    (
        DocumentType.MANUAL,
        (
            "manual",
            "kılavuz",
            "kilavuz",
            "user-guide",
            "handbook",
            "handbuch",
        ),
    ),
    (
        DocumentType.TRANSCRIPT,
        (
            "transcript",
            "transkript",
        ),
    ),
    (
        DocumentType.WORKSHEET,
        (
            "worksheet",
            "exercise",
            "exercises",
            "alistirma",
            "alıştırma",
            "workbook",
            "practice",
            "freebie",
        ),
    ),
    (
        DocumentType.GUIDE,
        (
            "guide",
            "rehber",
        ),
    ),
    (
        DocumentType.CHEATSHEET,
        (
            "cheatsheet",
            "cheat-sheet",
            "reference",
            "quick-reference",
        ),
    ),
]


GENERIC_DOCUMENT_KEYWORDS = (
    "document",
    "doc",
    "belge",
    "scan",
    "scanned",
)


def normalize_filename_for_matching(path: Path) -> str:
    stem = path.stem.lower()

    normalized = stem.replace("_", " ").replace("-", " ").replace(".", " ")
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def keyword_matches(normalized_name: str, keyword: str) -> bool:
    normalized_keyword = keyword.lower().replace("_", " ").replace("-", " ").strip()
    pattern = rf"(^|\s){re.escape(normalized_keyword)}($|\s)"

    return re.search(pattern, normalized_name) is not None


def classify_pdf_file(pdf_file: PdfFile) -> ClassifiedPdfFile:
    normalized_name = normalize_filename_for_matching(pdf_file.path)

    for document_type, keywords in KEYWORD_RULES:
        for keyword in keywords:
            if keyword_matches(normalized_name, keyword):
                return ClassifiedPdfFile(
                    pdf_file=pdf_file,
                    document_type=document_type,
                    confidence=0.9,
                    reason=f"Matched keyword: {keyword}",
                )

    for keyword in GENERIC_DOCUMENT_KEYWORDS:
        if keyword_matches(normalized_name, keyword):
            return ClassifiedPdfFile(
                pdf_file=pdf_file,
                document_type=DocumentType.DOCUMENT,
                confidence=0.3,
                reason=f"Matched generic keyword: {keyword}",
            )

    return ClassifiedPdfFile(
        pdf_file=pdf_file,
        document_type=DocumentType.UNKNOWN,
        confidence=0.0,
        reason="No filename keyword matched.",
    )


def classify_pdf_files(pdf_files: list[PdfFile]) -> list[ClassifiedPdfFile]:
    return [classify_pdf_file(pdf_file) for pdf_file in pdf_files]
