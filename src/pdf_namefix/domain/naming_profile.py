from dataclasses import dataclass
from pathlib import Path

import yaml


DEFAULT_NAMING_PROFILE = {
    "language": "english",
    "pattern": "{title}_{type}",
    "max_length": 120,
    "date_fallback": "none",
    "include_unknown_date_prefix": False,
    "include_type_suffix": True,
    "preserve_author_for_books": True,
    # Controls whether AI suggestions are safe enough to apply.
    "skip_if_confidence_below": 0.70,
    "ai_mode": "practical",
    "allow_known_work_inference": True,
    # Controls which deterministic suggestions should be sent to AI.
    "low_confidence_threshold": 0.70,
    "folders": {
        "book": "books",
        "ebook": "books",
        "reference": "reference",
        "language_learning": "language-learning",
        "study_material": "study-materials",
        "course": "courses",
        "worksheet": "worksheets",
        "article": "articles",
        "paper": "papers",
        "report": "reports",
        "payment": "payments",
        "invoice": "invoices",
        "exam": "exams",
        "document": "documents",
        "unknown": "needs-review",
    },
    "rules": [
        "Use lowercase snake_case filenames.",
        "Keep filenames short but descriptive.",
        "Do not invent dates.",
        "Do not add unknown-date unless the profile explicitly requires it.",
        "Do not include private personal identifiers unless they are already in the filename.",
        "Preserve .pdf extension.",
        "If the filename clearly matches a public book title and author, classify it as a book.",
        "Prefer specific types like book, guide, reference, language_learning, study_material over generic document.",
    ],
}


@dataclass(frozen=True)
class NamingProfile:
    language: str
    pattern: str
    max_length: int
    date_fallback: str
    include_unknown_date_prefix: bool
    include_type_suffix: bool
    preserve_author_for_books: bool
    skip_if_confidence_below: float
    ai_mode: str
    allow_known_work_inference: bool
    low_confidence_threshold: float
    folders: dict[str, str]
    rules: list[str]


def load_default_naming_profile() -> NamingProfile:
    return NamingProfile(
        language=str(DEFAULT_NAMING_PROFILE["language"]),
        pattern=str(DEFAULT_NAMING_PROFILE["pattern"]),
        max_length=int(DEFAULT_NAMING_PROFILE["max_length"]),
        date_fallback=str(DEFAULT_NAMING_PROFILE["date_fallback"]),
        include_unknown_date_prefix=bool(DEFAULT_NAMING_PROFILE["include_unknown_date_prefix"]),
        include_type_suffix=bool(DEFAULT_NAMING_PROFILE["include_type_suffix"]),
        preserve_author_for_books=bool(DEFAULT_NAMING_PROFILE["preserve_author_for_books"]),
        skip_if_confidence_below=float(DEFAULT_NAMING_PROFILE["skip_if_confidence_below"]),
        ai_mode=str(DEFAULT_NAMING_PROFILE["ai_mode"]),
        allow_known_work_inference=bool(DEFAULT_NAMING_PROFILE["allow_known_work_inference"]),
        low_confidence_threshold=float(DEFAULT_NAMING_PROFILE["low_confidence_threshold"]),
        folders=dict(DEFAULT_NAMING_PROFILE["folders"]),
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
        include_unknown_date_prefix=bool(
            data.get(
                "include_unknown_date_prefix",
                DEFAULT_NAMING_PROFILE["include_unknown_date_prefix"],
            )
        ),
        include_type_suffix=bool(
            data.get(
                "include_type_suffix",
                DEFAULT_NAMING_PROFILE["include_type_suffix"],
            )
        ),
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
        ai_mode=str(data.get("ai_mode", DEFAULT_NAMING_PROFILE["ai_mode"])),
        allow_known_work_inference=bool(
            data.get(
                "allow_known_work_inference",
                DEFAULT_NAMING_PROFILE["allow_known_work_inference"],
            )
        ),
        low_confidence_threshold=float(
            data.get(
                "low_confidence_threshold",
                DEFAULT_NAMING_PROFILE["low_confidence_threshold"],
            )
        ),
        folders=dict(data.get("folders", DEFAULT_NAMING_PROFILE["folders"])),
        rules=list(data.get("rules", DEFAULT_NAMING_PROFILE["rules"])),
    )
