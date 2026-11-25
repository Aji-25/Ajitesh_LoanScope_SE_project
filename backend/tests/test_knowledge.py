import pytest

from app.services.knowledge import chunk_text, clean_text, deterministic_embedding, parse_content


def test_clean_and_chunk_preserve_overlap() -> None:
    text = "  ".join(f"word{index}" for index in range(30))
    chunks = chunk_text(text, size=10, overlap=2)
    assert len(chunks) == 4
    assert chunks[0].split()[-2:] == chunks[1].split()[:2]
    assert "  " not in clean_text(text)


def test_deterministic_embedding_is_stable_and_normalized() -> None:
    first = deterministic_embedding("applicant identity verification")
    second = deterministic_embedding("applicant identity verification")
    assert first == second
    assert len(first) == 384
    assert abs(sum(value * value for value in first) - 1.0) < 0.00001


def test_related_text_shares_embedding_dimensions() -> None:
    identity = deterministic_embedding("identity evidence verification")
    related = deterministic_embedding("verify applicant identity evidence")
    dot_product = sum(left * right for left, right in zip(identity, related, strict=True))
    assert dot_product > 0.5


def test_irrelevant_text_has_no_embedding_similarity() -> None:
    policy = deterministic_embedding("applicant consent identity verification")
    irrelevant = deterministic_embedding("banana astronomy cooking")
    dot_product = sum(left * right for left, right in zip(policy, irrelevant, strict=True))
    assert dot_product == 0.0


@pytest.mark.parametrize(
    ("content_type", "data", "message"),
    [
        ("application/pdf", b"not a pdf", "PDF file is corrupt"),
        (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            b"not a docx",
            "DOCX file is corrupt",
        ),
        ("text/plain", b"", "document is empty"),
    ],
)
def test_parse_content_rejects_empty_or_corrupt_documents(
    content_type: str, data: bytes, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        parse_content(data, content_type)
