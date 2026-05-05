import re
import unicodedata
from pathlib import Path

from pdf_namefix.domain.models import ClassifiedPdfFile, FilenameSuggestion
from pdf_namefix.naming_profile import NamingProfile, load_default_naming_profile


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
    "unknown",
    "date",
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

    cleaned = re.sub(r"unknown[-_. ]date", " ", cleaned, flags=re.IGNORECASE)

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


def suggest_filename(
    classified_pdf_file: ClassifiedPdfFile,
    profile: NamingProfile | None = None,
) -> FilenameSuggestion:
    profile = profile or load_default_naming_profile()

    pdf_file = classified_pdf_file.pdf_file
    document_type = classified_pdf_file.document_type.value

    extracted_date = extract_date_from_name(pdf_file.path)
    title_slug = build_title_slug(pdf_file.path, document_type=document_type)

    # Date prefix logic based on profile
    if extracted_date != "unknown-date":
        prefix = f"{extracted_date}_"
    elif profile.include_unknown_date_prefix and profile.date_fallback != "none":
        prefix = f"{profile.date_fallback}_"
    else:
        prefix = ""

    # Type suffix logic based on profile
    if profile.include_type_suffix:
        filename = f"{prefix}{title_slug}_{document_type}.pdf"
    else:
        filename = f"{prefix}{title_slug}.pdf"

    suggested_name = clamp_filename(filename, profile.max_length)

    return FilenameSuggestion(
        classified_pdf_file=classified_pdf_file,
        suggested_name=suggested_name,
        reason="Built from filename date, cleaned title slug, and classified document type.",
    )


def split_pdf_filename(filename: str) -> tuple[str, str]:
    if filename.lower().endswith(".pdf"):
        return filename[:-4], ".pdf"

    path = Path(filename)
    return path.stem, path.suffix or ".pdf"


def build_suffixed_filename(filename: str, suffix_number: int) -> str:
    stem, suffix = split_pdf_filename(filename)
    return f"{stem}_{suffix_number}{suffix}"


def resolve_suggestion_collisions(
    suggestions: list[FilenameSuggestion],
    existing_names: set[str] | None = None,
) -> list[FilenameSuggestion]:
    existing_names = {name.lower() for name in existing_names or set()}

    used_names: set[str] = set(existing_names)
    original_counts: dict[str, int] = {}

    for suggestion in suggestions:
        key = suggestion.suggested_name.lower()
        original_counts[key] = original_counts.get(key, 0) + 1

    resolved: list[FilenameSuggestion] = []

    for suggestion in suggestions:
        original_name = suggestion.suggested_name
        original_key = original_name.lower()
        has_collision = (
            original_counts[original_key] > 1 or original_key in existing_names
        )

        candidate_name = original_name
        candidate_key = candidate_name.lower()
        suffix_number = 2

        while candidate_key in used_names:
            candidate_name = build_suffixed_filename(original_name, suffix_number)
            candidate_key = candidate_name.lower()
            suffix_number += 1

        used_names.add(candidate_key)

        resolved.append(
            FilenameSuggestion(
                classified_pdf_file=suggestion.classified_pdf_file,
                suggested_name=candidate_name,
                reason=(
                    suggestion.reason
                    if candidate_name == original_name
                    else f"{suggestion.reason} Collision resolved with numeric suffix."
                ),
                has_collision=has_collision,
                collision_group=original_name if has_collision else None,
                collision_resolved=has_collision and candidate_name != original_name,
                original_suggested_name=(
                    original_name if candidate_name != original_name else None
                ),
            )
        )

    return resolved


def suggest_filenames(
    classified_pdf_files: list[ClassifiedPdfFile],
    existing_names: set[str] | None = None,
    profile: NamingProfile | None = None,
) -> list[FilenameSuggestion]:
    profile = profile or load_default_naming_profile()

    suggestions = [
        suggest_filename(classified_pdf_file, profile=profile)
        for classified_pdf_file in classified_pdf_files
    ]

    return resolve_suggestion_collisions(
        suggestions=suggestions,
        existing_names=existing_names,
    )


def has_any_collision(suggestions: list[FilenameSuggestion]) -> bool:
    return any(suggestion.has_collision for suggestion in suggestions)
