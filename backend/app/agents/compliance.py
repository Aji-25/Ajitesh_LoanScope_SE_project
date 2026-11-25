from app.schemas.compliance import ComplianceAgentInput, ComplianceAssessment, PolicyMatch
from app.services.knowledge import numeric_values, relevance_terms

DIRECT_MATCH_CONFIDENCE = 0.85


class ComplianceAgent:
    def run(self, data: ComplianceAgentInput, match: PolicyMatch) -> ComplianceAssessment:
        selected = (
            data.evidence[match.passage - 1]
            if match.decision != "no_match" and 1 <= match.passage <= len(data.evidence)
            else None
        )
        terms = relevance_terms(data.requirement)
        overlap = terms & relevance_terms(selected.content) if selected else set()
        if selected is None or not overlap:
            return ComplianceAssessment(
                obligation="No matching policy evidence",
                applicability="unknown",
                rationale=match.reason
                if match.decision == "no_match"
                else ("The review did not identify a clause that supports this requirement."),
                evidence_chunk_ids=[],
                citations=[],
                confidence=0.0,
                gap_status="no_matching_evidence",
                human_review_required=False,
            )
        direct = (
            match.decision == "direct_match"
            and match.confidence >= DIRECT_MATCH_CONFIDENCE
            and numeric_values(data.requirement) <= numeric_values(selected.content)
            and len(overlap) >= min(2, len(terms))
        )
        return ComplianceAssessment(
            obligation=f"Matched policy clause in {selected.filename}",
            applicability="applicable" if direct else "needs_review",
            rationale=match.reason,
            evidence_chunk_ids=[selected.chunk_id],
            citations=[
                {
                    "chunk_id": str(selected.chunk_id),
                    "filename": selected.filename,
                    "section": selected.section,
                    "page": selected.page_number,
                    "version": selected.version,
                    "jurisdiction": selected.jurisdiction,
                    "excerpt": selected.content,
                }
            ],
            confidence=match.confidence,
            gap_status="ai_matched" if direct else "needs_human_review",
            human_review_required=not direct,
        )
