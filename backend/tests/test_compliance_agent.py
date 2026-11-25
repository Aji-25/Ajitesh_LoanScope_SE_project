import uuid

from app.agents.compliance import ComplianceAgent
from app.schemas.compliance import ComplianceAgentInput
from app.schemas.knowledge import EvidenceChunk


def test_compliance_agent_refuses_unsupported_claims() -> None:
    result = ComplianceAgent().run(
        ComplianceAgentInput(requirement="Retain consent evidence", evidence=[])
    )
    assert result.applicability == "unknown"
    assert result.evidence_chunk_ids == []
    assert result.confidence == 0.0
    assert result.gap_status == "insufficient_evidence"
    assert result.human_review_required is True


def test_compliance_agent_cites_retrieved_evidence() -> None:
    chunk_id = uuid.uuid4()
    evidence = EvidenceChunk(
        chunk_id=chunk_id,
        document_id=uuid.uuid4(),
        filename="Fair Lending Policy.txt",
        content="Consent evidence must be retained for audit.",
        page_number=2,
        section="Records",
        version="2.1",
        jurisdiction="India",
        effective_date=None,
        score=0.88,
    )
    result = ComplianceAgent().run(
        ComplianceAgentInput(requirement="Retain consent evidence", evidence=[evidence])
    )
    assert result.evidence_chunk_ids == [chunk_id]
    assert result.citations[0]["section"] == "Records"
    assert result.confidence == 0.88
    assert result.gap_status == "review_required"
