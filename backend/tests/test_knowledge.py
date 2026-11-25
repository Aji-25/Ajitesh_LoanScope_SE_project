import uuid
from unittest.mock import AsyncMock, Mock

import pytest

from app.schemas.knowledge import EvidenceAnswer, EvidenceChunk, RetrievalResponse
from app.services.knowledge import (
    KnowledgeService,
    chunk_text,
    clean_text,
    deterministic_embedding,
    numeric_values,
    parse_content,
    policy_clauses,
)


@pytest.mark.parametrize(
    ("query", "has_answer"),
    [
        ("When is applicant consent required?", True),
        ("What does clause CONSENT-1 say?", True),
        ("When can an applicant withdraw consent?", False),
        ("What does clause CONSENT-10 say?", False),
    ],
)
async def test_policy_answer_recovers_only_direct_evidence(
    monkeypatch: pytest.MonkeyPatch, query: str, has_answer: bool
) -> None:
    clause = EvidenceChunk(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        filename="policy.txt",
        content=(
            "Section CONSENT-1 Applicant Consent. Explicit applicant consent must be "
            "collected before personal or financial information is stored for underwriting."
        ),
        page_number=1,
        section="Chunk 1",
        version="1",
        jurisdiction="India",
        effective_date=None,
        score=0.9,
    )
    knowledge = KnowledgeService(Mock(commit=AsyncMock()))
    monkeypatch.setattr(
        knowledge, "retrieve", AsyncMock(return_value=RetrievalResponse(items=[clause]))
    )
    model = Mock(structured_generate=AsyncMock(return_value=EvidenceAnswer(source=0, answer="")))
    monkeypatch.setattr("app.services.knowledge.get_live_llm_service", lambda: model)

    result = await knowledge.answer(uuid.uuid4(), uuid.uuid4(), query, 5)

    assert result is not None
    assert result.answer == (clause.content if has_answer else None)
    assert result.answer_source == (clause if has_answer else None)
    model.structured_generate.assert_awaited_once()


def test_clean_and_chunk_preserve_overlap() -> None:
    text = "  ".join(f"word{index}" for index in range(30))
    chunks = chunk_text(text, size=10, overlap=2)
    assert len(chunks) == 4
    assert chunks[0].split()[-2:] == chunks[1].split()[:2]
    assert "  " not in clean_text(text)


def test_policy_clauses_split_a_legacy_chunk_without_changing_amounts() -> None:
    text = "Store consent. Applications above INR 500,000 require underwriting."
    assert policy_clauses(text) == [
        "Store consent.",
        "Applications above INR 500,000 require underwriting.",
    ]
    assert numeric_values(text) == numeric_values("500000")


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
