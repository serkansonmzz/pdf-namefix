import re
import unicodedata
from pathlib import Path

from pdf_namefix.models import ClassifiedPdfFile, FilenameSuggestion


DATE_PATTERNS = [
    # 2026-04-29, 2026_04_29, 2026.04.29
    re.compile(r"(?P<year>20\d{2})[-_. ](?P<month>\d{1,2})[-_. ](?P<day>\d{1,2})"),
    # 29-04-2026, 29_04_2026, 29.04.2026
    re.compile(r"(?P<day>\d{1,2})[-_. ](?P<month>\d{1,2})[-_. ](?P<year>20\d{2})"),
    # 20260429
    re.compile(r"(?P<year>20\d{2})(?P<month>\d{2})(?P<day>\d{2})"),
]


NOISE_WORDS = {
    "pdf",
    "document",
    "doc",
    "scan",
    "scanned",
    "final",
    "copy",
    "new",
    "old",
    "v1",
    "v2",
    "v3",
}


def extract_date_from_name(path: Path) -> str:
    normalized = path.stem

    for pattern in DATE_PATTERNS:
        match = pattern.search(normalized)
        if not match:
            continue

        year = int(match.group("year"))
        month = int(match.group("month"))
        day = int(match.group("day"))

        if not (1 <= month <= 12 and 1 <= day <= 31):
            continue

        return f"{year:04d}-{month:02d}-{day:02d}"

    return "unknown-date"


def strip_date_patterns(text: str) -> str:
    cleaned = text

    for pattern in DATE_PATTERNS:
        cleaned = pattern.sub(" ", cleaned)

    return cleaned


def normalize_to_ascii(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("ascii")


def slugify_filename_part(text: str) -> str:
    ascii_text = normalize_to_ascii(text.lower())
    ascii_text = ascii_text.replace("&", " and ")

    cleaned = re.sub(r"[^a-z0-9]+", "_", ascii_text)
    cleaned = re.sub(r"_+", "_", cleaned)
    cleaned = cleaned.strip("_")

    return cleaned


def build_title_slug(path: Path, document_type: str) -> str:
    stem = strip_date_patterns(path.stem)
    slug = slugify_filename_part(stem)

    if not slug:
        return "unknown"

    parts = [part for part in slug.split("_") if part and part not in NOISE_WORDS]

    if parts and parts[-1] == document_type:
        parts = parts[:-1]

    if not parts:
        return "unknown"

    return "_".join(parts)


def clamp_filename(filename: str, max_length: int = 120) -> str:
    if len(filename) <= max_length:
        return filename

    suffix = ".pdf"

    if not filename.endswith(suffix):
        return filename[:max_length]

    available = max_length - len(suffix)
    return f"{filename[:available].rstrip('_')}{suffix}"


def suggest_filename(classified_pdf_file: ClassifiedPdfFile) -> FilenameSuggestion:
    pdf_file = classified_pdf_file.pdf_file
    document_type = classified_pdf_file.document_type.value

    date_part = extract_date_from_name(pdf_file.path)
    title_slug = build_title_slug(pdf_file.path, document_type=document_type)

    suggested_name = f"{date_part}_{title_slug}_{document_type}.pdf"
    suggested_name = clamp_filename(suggested_name)

    return FilenameSuggestion(
        classified_pdf_file=classified_pdf_file,
        suggested_name=suggested_name,
        reason="Built from filename date, cleaned title slug, and classified document type.",
    )


def mark_collisions(
    suggestions: list[FilenameSuggestion],
) -> list[FilenameSuggestion]:
    name_counts: dict[str, int] = {}

    for suggestion in suggestions:
        name_counts[suggestion.suggested_name] = (
            name_counts.get(suggestion.suggested_name, 0) + 1
        )

    updated: list[FilenameSuggestion] = []

    for suggestion in suggestions:
        has_collision = name_counts[suggestion.suggested_name] > 1

        updated.append(
            FilenameSuggestion(
                classified_pdf_file=suggestion.classified_pdf_file,
                suggested_name=suggestion.suggested_name,
                reason=suggestion.reason,
                has_collision=has_collision,
                collision_group=suggestion.suggested_name if has_collision else None,
            )
        )

    return updated


def suggest_filenames(
    classified_pdf_files: list[ClassifiedPdfFile],
) -> list[FilenameSuggestion]:
    suggestions = [
        suggest_filename(classified_pdf_file)
        for classified_pdf_file in classified_pdf_files
    ]

    return mark_collisions(suggestions)
