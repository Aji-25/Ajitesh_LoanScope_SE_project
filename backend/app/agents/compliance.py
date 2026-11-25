from app.schemas.compliance import ComplianceAgentInput, ComplianceAssessment


class ComplianceAgent:
    """Maps obligations only when retrieved source evidence is supplied."""

    def run(self, data: ComplianceAgentInput) -> ComplianceAssessment:
        if not data.evidence:
            return ComplianceAssessment(
                obligation="No grounded obligation identified",
                applicability="unknown",
                rationale="No retrieved evidence supports a regulatory conclusion.",
                evidence_chunk_ids=[],
                citations=[],
                confidence=0.0,
                gap_status="insufficient_evidence",
                human_review_required=True,
            )
        strongest = data.evidence[0]
        return ComplianceAssessment(
            obligation=f"Review requirement against {strongest.filename}",
            applicability="applicable",
            rationale=(
                "The retrieved source contains language relevant to the requirement. "
                "A compliance officer must confirm the interpretation."
            ),
            evidence_chunk_ids=[item.chunk_id for item in data.evidence],
            citations=[
                {
                    "filename": item.filename,
                    "section": item.section,
                    "page": item.page_number,
                    "version": item.version,
                    "jurisdiction": item.jurisdiction,
                }
                for item in data.evidence
            ],
            confidence=min(0.95, strongest.score),
            gap_status="review_required",
            human_review_required=True,
        )
