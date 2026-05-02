from pathlib import Path

from pypdf import PdfReader

from pdf_namefix.models import PdfFile, PdfInsights


MAX_FIRST_PAGE_TEXT_CHARS = 3000


def safe_str(value: object) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    return text or None


def truncate_text(text: str | None, max_chars: int = MAX_FIRST_PAGE_TEXT_CHARS) -> str | None:
    if text is None:
        return None

    cleaned = " ".join(text.split())

    if not cleaned:
        return None

    return cleaned[:max_chars]


def inspect_pdf_file(pdf_file: PdfFile) -> PdfInsights:
    path = pdf_file.path

    try:
        reader = PdfReader(str(path), strict=False)

        metadata = reader.metadata
        page_count = len(reader.pages)

        first_page_text: str | None = None

        if page_count > 0:
            try:
                first_page_text = reader.pages[0].extract_text()
            except Exception as exc:
                return PdfInsights(
                    path=path,
                    page_count=page_count,
                    extraction_error=f"First page text extraction failed: {exc}",
                )

        return PdfInsights(
            path=path,
            page_count=page_count,
            metadata_title=safe_str(getattr(metadata, "title", None)) if metadata else None,
            metadata_author=safe_str(getattr(metadata, "author", None)) if metadata else None,
            metadata_subject=safe_str(getattr(metadata, "subject", None)) if metadata else None,
            metadata_creator=safe_str(getattr(metadata, "creator", None)) if metadata else None,
            metadata_producer=safe_str(getattr(metadata, "producer", None)) if metadata else None,
            metadata_creation_date=safe_str(getattr(metadata, "creation_date", None)) if metadata else None,
            first_page_text=truncate_text(first_page_text),
        )

    except Exception as exc:
        return PdfInsights(
            path=path,
            extraction_error=str(exc),
        )


def inspect_pdf_files(pdf_files: list[PdfFile]) -> dict[Path, PdfInsights]:
    return {
        pdf_file.path: inspect_pdf_file(pdf_file)
        for pdf_file in pdf_files
    }
