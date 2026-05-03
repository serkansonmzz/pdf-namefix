from pdf_namefix.naming_profile import load_default_naming_profile, load_naming_profile


def test_load_default_naming_profile():
    profile = load_default_naming_profile()

    assert profile.language == "english"
    assert profile.pattern == "{date}_{title}_{type}"
    assert profile.max_length == 120
    assert profile.skip_if_confidence_below == 0.70


def test_load_naming_profile_from_yaml(tmp_path):
    path = tmp_path / "profile.yml"
    path.write_text(
        """
language: english
pattern: "{date}_{title}_{type}"
max_length: 90
date_fallback: "unknown-date"
preserve_author_for_books: false
skip_if_confidence_below: 0.8
rules:
  - Keep names short.
""",
        encoding="utf-8",
    )

    profile = load_naming_profile(path)

    assert profile.max_length == 90
    assert profile.preserve_author_for_books is False
    assert profile.skip_if_confidence_below == 0.8
    assert profile.rules == ["Keep names short."]


def test_load_naming_profile_empty_yaml_uses_defaults(tmp_path):
    path = tmp_path / "profile.yml"
    path.write_text("", encoding="utf-8")

    profile = load_naming_profile(path)

    assert profile.language == "english"
    assert profile.max_length == 120
