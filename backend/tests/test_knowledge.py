from app.services.knowledge import chunk_text, clean_text, deterministic_embedding


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
