import json
import re
from typing import Any, Protocol

from openai import OpenAI

from pdf_namefix.models import AiNamingInput, AiNamingSuggestion, DocumentType, FilenameSuggestion
from pdf_namefix.naming_profile import NamingProfile


AI_NAMING_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "ai_suggested_name": {
            "type": "string",
            "description": "Improved safe PDF filename ending with .pdf.",
        },
        "ai_document_type": {
            "type": "string",
            "enum": [document_type.value for document_type in DocumentType],
        },
        "semantic_type": {
            "type": "string",
            "description": "More specific human-readable semantic type, e.g. public_book, technical_setup_guide.",
        },
        "confidence": {
            "type": "number",
        },
        "reason": {
            "type": "string",
        },
        "improvement": {
            "type": "string",
            "description": "Explain what improved compared with the current deterministic suggestion.",
        },
        "should_apply": {
            "type": "boolean",
        },
    },
    "required": [
        "ai_suggested_name",
        "ai_document_type",
        "semantic_type",
        "confidence",
        "reason",
        "improvement",
        "should_apply",
    ],
}


class AiNamingClient(Protocol):
    def suggest_name(
        self,
        naming_input: AiNamingInput,
        profile: NamingProfile,
        model: str,
    ) -> AiNamingSuggestion:
        ...


def sanitize_ai_filename(filename: str, max_length: int) -> str:
    cleaned = filename.strip()

    if not cleaned.lower().endswith(".pdf"):
        cleaned = f"{cleaned}.pdf"

    cleaned = cleaned.replace("/", "_").replace("\\", "_")
    cleaned = cleaned.lower()
    cleaned = re.sub(r"[^a-z0-9._-]+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned)
    cleaned = cleaned.strip("_")

    if not cleaned:
        cleaned = "unknown.pdf"

    if len(cleaned) <= max_length:
        return cleaned

    suffix = ".pdf"
    available = max(max_length - len(suffix), 1)

    return f"{cleaned[:available].rstrip('_')}{suffix}"


def clamp_confidence(value: float) -> float:
    return max(0.0, min(1.0, value))


def build_ai_prompt(
    naming_input: AiNamingInput,
    profile: NamingProfile,
) -> str:
    rules = "\n".join(f"- {rule}" for rule in profile.rules)

    return f"""
You are helping rename local PDF files safely.

Return only a structured JSON object matching the schema.

Goal:
Improve the current deterministic filename suggestion when there is enough evidence.

Naming profile:
- language: {profile.language}
- pattern: {profile.pattern}
- max_length: {profile.max_length}
- date_fallback: {profile.date_fallback}
- include_unknown_date_prefix: {profile.include_unknown_date_prefix}
- include_type_suffix: {profile.include_type_suffix}
- preserve_author_for_books: {profile.preserve_author_for_books}
- skip_if_confidence_below: {profile.skip_if_confidence_below}
- ai_mode: {profile.ai_mode}
- allow_known_work_inference: {profile.allow_known_work_inference}

Rules:
{rules}

Current deterministic result:
- source_name: {naming_input.source_name}
- current_document_type: {naming_input.current_document_type.value}
- current_confidence: {naming_input.current_confidence}
- current_suggested_name: {naming_input.current_suggested_name}

PDF metadata/text signals:
- metadata_title: {naming_input.metadata_title}
- metadata_author: {naming_input.metadata_author}
- metadata_subject: {naming_input.metadata_subject}
- first_page_text: {naming_input.first_page_text}

Important behavior:
- Do not invent dates. If profile.date_fallback is "none", do not add a date prefix.
- Only add unknown-date prefix if include_unknown_date_prefix is true and date_fallback is not "none".
- Prefer the original filename title when it is meaningful.
- Treat PDF metadata title as a supporting signal, not always as the main title.
- If metadata title looks generic, unrelated, or weaker than the filename, do not use it in the suggested filename.
- Do not replace a clear filename topic with a vague metadata title.
- Do not use generic document if a more specific type is reasonably clear.
- If filename clearly contains a known public book title or title + author, you may classify it as book.
- If it is a technical setup/tutorial document, prefer guide or study_material.
- If it is about language learning, grammar, vocabulary, IELTS, TOEFL, speaking, listening, prefer language_learning or reference.
- Keep the original meaningful title unless there is a clear improvement.
- Explain exactly what improved over current_suggested_name.
- Set should_apply=true only if confidence >= {profile.skip_if_confidence_below}.
- Confidence must be between 0 and 1.

Examples:
- How-To-Lie-With-Statistics.pdf is likely a public book title. A good name is unknown-date_how_to_lie_with_statistics_darrell_huff_book.pdf if the author is known or strongly indicated.
- The-war-of-art-by-Robert-Pressfield.pdf is likely a public book title with author. A good name is unknown-date_the_war_of_art_robert_pressfield_book.pdf.
- Neovim-ve-Tmux-kurulumu.pdf is likely a technical setup guide. A good name is unknown-date_neovim_tmux_setup_guide.pdf.
- SSH-Key-ve-Vps-ayarları.pdf is likely a technical setup guide. A good name is ssh_key_vps_setup_guide.pdf. Do not replace the clear filename topic with weak metadata like "vite project" unless the content clearly requires it.
""".strip()


class OpenAiNamingClient:
    def __init__(self, client: Any | None = None) -> None:
        self.client = client or OpenAI()

    def suggest_name(
        self,
        naming_input: AiNamingInput,
        profile: NamingProfile,
        model: str,
    ) -> AiNamingSuggestion:
        prompt = build_ai_prompt(naming_input=naming_input, profile=profile)

        response = self.client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": "You generate safe PDF filename suggestions as JSON.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "ai_naming_suggestion",
                    "strict": True,
                    "schema": AI_NAMING_SCHEMA,
                }
            },
        )

        data = json.loads(response.output_text)

        ai_document_type = DocumentType(data["ai_document_type"])
        ai_suggested_name = sanitize_ai_filename(
            data["ai_suggested_name"],
            max_length=profile.max_length,
        )

        confidence = clamp_confidence(float(data["confidence"]))
        should_apply = bool(data["should_apply"]) and confidence >= profile.skip_if_confidence_below

        return AiNamingSuggestion(
            source_path=naming_input.source_path,
            source_name=naming_input.source_name,
            current_suggested_name=naming_input.current_suggested_name,
            current_document_type=naming_input.current_document_type,
            current_confidence=naming_input.current_confidence,
            ai_suggested_name=ai_suggested_name,
            ai_document_type=ai_document_type,
            semantic_type=str(data["semantic_type"]),
            confidence=confidence,
            reason=str(data["reason"]),
            improvement=str(data["improvement"]),
            should_apply=should_apply,
        )


def select_ai_candidates(
    suggestions: list[FilenameSuggestion],
    unknown_only: bool = False,
    low_confidence: bool = False,
    threshold: float = 0.70,
) -> list[FilenameSuggestion]:
    selected: list[FilenameSuggestion] = []

    for suggestion in suggestions:
        classified = suggestion.classified_pdf_file

        is_unknown = classified.document_type == DocumentType.UNKNOWN
        is_low_confidence = classified.confidence < threshold

        if unknown_only and not is_unknown:
            continue

        if low_confidence and not is_low_confidence:
            continue

        if not unknown_only and not low_confidence:
            selected.append(suggestion)
            continue

        selected.append(suggestion)

    return selected
