from pathlib import Path

from pdf_namefix.domain.models import DocumentType
from pdf_namefix.infrastructure.type_resolver import document_type_from_filename_suffix


def test_resolves_study_material_suffix():
    assert (
        document_type_from_filename_suffix(
            Path("baglantili_not_almanin_faydasi_study_material.pdf")
        )
        == DocumentType.STUDY_MATERIAL
    )


def test_resolves_language_learning_suffix():
    assert (
        document_type_from_filename_suffix(
            Path("morphological_contrastive_language_learning.pdf")
        )
        == DocumentType.LANGUAGE_LEARNING
    )


def test_resolves_payment_suffix():
    assert (
        document_type_from_filename_suffix(Path("fonksiyonlar_quiz_payment.pdf"))
        == DocumentType.PAYMENT
    )


def test_returns_none_for_untyped_filename():
    assert document_type_from_filename_suffix(Path("random.pdf")) is None
