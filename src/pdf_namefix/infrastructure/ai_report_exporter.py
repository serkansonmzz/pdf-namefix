import json
from datetime import datetime, timezone
from pathlib import Path

from pdf_namefix.domain.ai_models import AiNamingSuggestion


def ai_suggestion_to_dict(suggestion: AiNamingSuggestion) -> dict:
    return {
        "source_path": str(suggestion.source_path),
        "source_name": suggestion.source_name,
        "current": {
            "suggested_name": suggestion.current_suggested_name,
            "document_type": suggestion.current_document_type.value,
            "confidence": suggestion.current_confidence,
        },
        "ai": {
            "suggested_name": suggestion.ai_suggested_name,
            "document_type": suggestion.ai_document_type.value,
            "semantic_type": suggestion.semantic_type,
            "confidence": suggestion.confidence,
            "reason": suggestion.reason,
            "improvement": suggestion.improvement,
            "should_apply": suggestion.should_apply,
        },
    }


def render_ai_json_report(
    suggestions: list[AiNamingSuggestion],
    model: str,
) -> str:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "suggestions": [
            ai_suggestion_to_dict(suggestion)
            for suggestion in suggestions
        ],
    }

    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_ai_markdown_report(
    suggestions: list[AiNamingSuggestion],
    model: str,
) -> str:
    lines: list[str] = []

    lines.append("# pdf-namefix AI Suggestions")
    lines.append("")
    lines.append(f"Generated at: `{datetime.now(timezone.utc).isoformat()}`")
    lines.append(f"Model: `{model}`")
    lines.append("")
    lines.append("## Suggestions")
    lines.append("")
    lines.append(
        "| # | File | Current type | AI type | Current name | AI name | Confidence | Apply? | Improvement |"
    )
    lines.append(
        "|---:|---|---|---|---|---|---:|---|---|"
    )

    for index, suggestion in enumerate(suggestions, start=1):
        lines.append(
            "| "
            f"{index} | "
            f"`{suggestion.source_name}` | "
            f"{suggestion.current_document_type.value} | "
            f"{suggestion.ai_document_type.value} / {suggestion.semantic_type} | "
            f"`{suggestion.current_suggested_name}` | "
            f"`{suggestion.ai_suggested_name}` | "
            f"{suggestion.confidence:.2f} | "
            f"{'yes' if suggestion.should_apply else 'no'} | "
            f"{suggestion.improvement} |"
        )

    lines.append("")
    lines.append("## Reasons")
    lines.append("")

    for suggestion in suggestions:
        lines.append(f"### {suggestion.source_name}")
        lines.append("")
        lines.append(f"- Reason: {suggestion.reason}")
        lines.append(f"- Improvement: {suggestion.improvement}")
        lines.append("")

    return "\n".join(lines)


def write_ai_report(
    suggestions: list[AiNamingSuggestion],
    model: str,
    out_path: Path,
    output_format: str,
    overwrite: bool = False,
) -> Path:
    if out_path.exists() and not overwrite:
        raise FileExistsError(f"AI suggestion report already exists: {out_path}")

    if output_format == "json":
        content = render_ai_json_report(suggestions=suggestions, model=model)
    elif output_format == "markdown":
        content = render_ai_markdown_report(suggestions=suggestions, model=model)
    else:
        raise ValueError(f"Unsupported AI report format: {output_format}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")

    return out_path
