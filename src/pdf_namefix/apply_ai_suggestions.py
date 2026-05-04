import json
from pathlib import Path

from pdf_namefix.models import DocumentType, FilenameSuggestion


def load_ai_suggestion_map(path: Path) -> dict[Path, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))

    mapping: dict[Path, dict] = {}

    for item in data.get("suggestions", []):
        source_path = Path(item["source_path"])
        mapping[source_path] = item["ai"]

    return mapping


def apply_ai_suggestions_to_filename_suggestions(
    suggestions: list[FilenameSuggestion],
    ai_map: dict[Path, dict],
    min_confidence: float = 0.80,
) -> list[FilenameSuggestion]:
    updated: list[FilenameSuggestion] = []

    for suggestion in suggestions:
        classified = suggestion.classified_pdf_file
        pdf_file = classified.pdf_file
        ai = ai_map.get(pdf_file.path)

        if not ai:
            updated.append(suggestion)
            continue

        confidence = float(ai.get("confidence", 0.0))
        should_apply = bool(ai.get("should_apply", False))

        if not should_apply or confidence < min_confidence:
            updated.append(suggestion)
            continue

        ai_name = str(ai["suggested_name"])
        ai_type = DocumentType(str(ai["document_type"]))

        updated_classified = type(classified)(
            pdf_file=classified.pdf_file,
            document_type=ai_type,
            confidence=confidence,
            reason=f"AI suggestion: {ai.get('reason', '')}",
        )

        updated.append(
            FilenameSuggestion(
                classified_pdf_file=updated_classified,
                suggested_name=ai_name,
                reason=f"AI suggestion applied: {ai.get('improvement', '')}",
                has_collision=suggestion.has_collision,
                collision_group=suggestion.collision_group,
                collision_resolved=suggestion.collision_resolved,
                original_suggested_name=suggestion.suggested_name,
            )
        )

    return updated
