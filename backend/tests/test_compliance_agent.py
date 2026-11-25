import uuid

from app.agents.compliance import ComplianceAgent
from app.schemas.compliance import ComplianceAgentInput, PolicyMatch
from app.schemas.knowledge import EvidenceChunk

REQUIREMENT = "Every application above INR 500,000 requires manual underwriting approval."


def review(clause: str) -> ComplianceAgentInput:
    return ComplianceAgentInput(
        requirement=REQUIREMENT,
        evidence=[
            EvidenceChunk(
                chunk_id=uuid.uuid4(),
                document_id=uuid.uuid4(),
                filename="Policy.txt",
                content=clause,
                page_number=None,
                section="Underwriting",
                version="1.0",
                jurisdiction="India",
                effective_date=None,
                score=0.8,
            )
        ],
    )


def test_clear_match_quotes_clause_without_human_review() -> None:
    data = review(REQUIREMENT)
    result = ComplianceAgent().run(
        data,
        PolicyMatch(
            requirement_code="REQ-005",
            decision="direct_match",
            passage=1,
            confidence=0.95,
            reason="The source contains the same threshold and approval rule.",
        ),
    )
    assert result.gap_status == "ai_matched"
    assert result.human_review_required is False
    assert result.citations[0]["excerpt"] == REQUIREMENT


def test_different_amount_cannot_be_marked_as_a_direct_match() -> None:
    data = review(REQUIREMENT.replace("500,000", "400,000"))
    result = ComplianceAgent().run(
        data,
        PolicyMatch(
            requirement_code="REQ-005",
            decision="direct_match",
            passage=1,
            confidence=0.98,
            reason="The topic relates to manual underwriting.",
        ),
    )
    assert result.gap_status == "needs_human_review"
    assert result.human_review_required is True


def test_no_match_discards_any_selected_passage() -> None:
    data = review("Retain records of consent.")
    result = ComplianceAgent().run(
        data,
        PolicyMatch(
            requirement_code="REQ-005",
            decision="no_match",
            passage=1,
            confidence=0.9,
            reason="The source only discusses a consent record.",
        ),
    )
    assert result.gap_status == "no_matching_evidence"
    assert result.evidence_chunk_ids == []
    assert result.human_review_required is False
