from dataclasses import dataclass
from pathlib import Path

import yaml


DEFAULT_NAMING_PROFILE = {
    "language": "english",
    "pattern": "{date}_{title}_{type}",
    "max_length": 120,
    "date_fallback": "unknown-date",
    "preserve_author_for_books": True,
    "skip_if_confidence_below": 0.70,
    "rules": [
        "Use lowercase snake_case filenames.",
        "Keep filenames short but descriptive.",
        "Do not invent dates.",
        "Use unknown-date if no reliable date is available.",
        "Do not include private personal identifiers unless they are already in the filename.",
        "Preserve .pdf extension.",
    ],
}


@dataclass(frozen=True)
class NamingProfile:
    language: str
    pattern: str
    max_length: int
    date_fallback: str
    preserve_author_for_books: bool
    skip_if_confidence_below: float
    rules: list[str]


def load_default_naming_profile() -> NamingProfile:
    return NamingProfile(
        language=str(DEFAULT_NAMING_PROFILE["language"]),
        pattern=str(DEFAULT_NAMING_PROFILE["pattern"]),
        max_length=int(DEFAULT_NAMING_PROFILE["max_length"]),
        date_fallback=str(DEFAULT_NAMING_PROFILE["date_fallback"]),
        preserve_author_for_books=bool(DEFAULT_NAMING_PROFILE["preserve_author_for_books"]),
        skip_if_confidence_below=float(DEFAULT_NAMING_PROFILE["skip_if_confidence_below"]),
        rules=list(DEFAULT_NAMING_PROFILE["rules"]),
    )


def load_naming_profile(path: Path | None = None) -> NamingProfile:
    if path is None:
        return load_default_naming_profile()

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    return NamingProfile(
        language=str(data.get("language", DEFAULT_NAMING_PROFILE["language"])),
        pattern=str(data.get("pattern", DEFAULT_NAMING_PROFILE["pattern"])),
        max_length=int(data.get("max_length", DEFAULT_NAMING_PROFILE["max_length"])),
        date_fallback=str(data.get("date_fallback", DEFAULT_NAMING_PROFILE["date_fallback"])),
        preserve_author_for_books=bool(
            data.get(
                "preserve_author_for_books",
                DEFAULT_NAMING_PROFILE["preserve_author_for_books"],
            )
        ),
        skip_if_confidence_below=float(
            data.get(
                "skip_if_confidence_below",
                DEFAULT_NAMING_PROFILE["skip_if_confidence_below"],
            )
        ),
        rules=list(data.get("rules", DEFAULT_NAMING_PROFILE["rules"])),
    )
