import json
from pathlib import Path

from pdf_namefix.ai_naming import (
    OpenAiNamingClient,
    build_ai_prompt,
    sanitize_ai_filename,
)
from pdf_namefix.models import AiNamingInput, DocumentType
from pdf_namefix.naming_profile import load_default_naming_profile


class FakeResponse:
    output_text = json.dumps(
        {
            "suggested_name": "Essential Grammar in Use / Cambridge.pdf",
            "document_type": "language_learning",
            "confidence": 0.82,
            "reason": "Metadata and first page mention the title and publisher.",
            "should_apply": True,
        }
    )


class FakeResponses:
    def __init__(self) -> None:
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return FakeResponse()


class FakeOpenAI:
    def __init__(self) -> None:
        self.responses = FakeResponses()


def make_input() -> AiNamingInput:
    return AiNamingInput(
        source_path=Path("File0001.pdf"),
        source_name="File0001.pdf",
        current_document_type=DocumentType.UNKNOWN,
        current_confidence=0.0,
        current_suggested_name="unknown-date_file0001_unknown.pdf",
        metadata_title="Essential Grammar in Use",
        metadata_author="Raymond Murphy",
        metadata_subject="English grammar reference",
        first_page_text="Essential Grammar in Use Cambridge University Press",
    )


def test_sanitize_ai_filename_adds_pdf_suffix():
    assert sanitize_ai_filename("test_file", max_length=120) == "test_file.pdf"


def test_sanitize_ai_filename_removes_path_separators():
    assert sanitize_ai_filename("../bad/name.pdf", max_length=120) == ".._bad_name.pdf"


def test_sanitize_ai_filename_clamps_length():
    filename = sanitize_ai_filename(f"{'a' * 200}.pdf", max_length=120)

    assert len(filename) <= 120
    assert filename.endswith(".pdf")


def test_build_ai_prompt_contains_profile_and_input():
    profile = load_default_naming_profile()
    prompt = build_ai_prompt(make_input(), profile)

    assert "Essential Grammar in Use" in prompt
    assert "unknown-date_file0001_unknown.pdf" in prompt
    assert "Do not invent dates" in prompt


def test_openai_naming_client_parses_structured_output():
    fake_client = FakeOpenAI()
    profile = load_default_naming_profile()
    client = OpenAiNamingClient(client=fake_client)

    suggestion = client.suggest_name(
        naming_input=make_input(),
        profile=profile,
        model="test-model",
    )

    assert suggestion.source_path == Path("File0001.pdf")
    assert suggestion.suggested_name == "essential_grammar_in_use_cambridge.pdf"
    assert suggestion.document_type == DocumentType.LANGUAGE_LEARNING
    assert suggestion.confidence == 0.82
    assert suggestion.should_apply is True
    assert fake_client.responses.last_kwargs["text"]["format"]["type"] == "json_schema"
