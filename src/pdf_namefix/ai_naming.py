import json
import re
from typing import Any, Protocol

from openai import OpenAI

from pdf_namefix.models import AiNamingInput, AiNamingSuggestion, DocumentType
from pdf_namefix.naming_profile import NamingProfile


AI_NAMING_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "suggested_name": {
            "type": "string",
            "description": "Suggested safe PDF filename ending with .pdf.",
        },
        "document_type": {
            "type": "string",
            "enum": [document_type.value for document_type in DocumentType],
        },
        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
        },
        "reason": {
            "type": "string",
        },
        "should_apply": {
            "type": "boolean",
        },
    },
    "required": [
        "suggested_name",
        "document_type",
        "confidence",
        "reason",
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


def build_ai_prompt(
    naming_input: AiNamingInput,
    profile: NamingProfile,
) -> str:
    rules = "\n".join(f"- {rule}" for rule in profile.rules)

    return f"""
You are helping rename local PDF files safely.

Return only a structured JSON object matching the schema.

Naming profile:
- language: {profile.language}
- pattern: {profile.pattern}
- max_length: {profile.max_length}
- date_fallback: {profile.date_fallback}
- preserve_author_for_books: {profile.preserve_author_for_books}
- skip_if_confidence_below: {profile.skip_if_confidence_below}

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

Instructions:
- Suggest a safer, clearer filename.
- Do not invent a date.
- Use unknown-date if no reliable date exists.
- Preserve .pdf extension.
- If confidence is below the profile threshold, set should_apply=false.
- If there is not enough information, keep should_apply=false.
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

        document_type = DocumentType(data["document_type"])
        suggested_name = sanitize_ai_filename(
            str(data["suggested_name"]),
            max_length=profile.max_length,
        )

        confidence = min(max(float(data["confidence"]), 0.0), 1.0)
        should_apply = bool(data["should_apply"]) and confidence >= profile.skip_if_confidence_below

        return AiNamingSuggestion(
            source_path=naming_input.source_path,
            suggested_name=suggested_name,
            document_type=document_type,
            confidence=confidence,
            reason=str(data["reason"]),
            should_apply=should_apply,
        )
