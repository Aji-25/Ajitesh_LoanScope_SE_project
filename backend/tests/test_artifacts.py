from io import BytesIO
from types import SimpleNamespace
from typing import Any, cast

from pypdf import PdfReader

from app.models.database import Project, Requirement
from app.services.artifact_pdf import render_artifact_pdf
from app.services.artifacts import build_artifact_payloads


def inputs() -> tuple[Project, Requirement]:
    project = Project(
        name="Loan Intake",
        summary="Digital personal loan origination",
        product_type="Personal loans",
        jurisdiction="India",
    )
    requirement = cast(
        Requirement,
        SimpleNamespace(
            id="id-1",
            requirement_code="REQ-007",
            statement="The system shall capture consent.",
            source_stakeholder="Compliance Officer",
            categories=["Privacy"],
            priority=None,
            assumptions=[],
            dependencies=[],
            acceptance_criteria=["Consent is timestamped"],
            approval_status="approved",
            quality_findings=[],
        ),
    )
    return project, requirement


def test_artifact_set_contains_all_required_outputs() -> None:
    project, requirement = inputs()
    payloads = build_artifact_payloads(project, [requirement], [], [], None)
    assert {item[0] for item in payloads} == {
        "srs",
        "user_stories",
        "acceptance_criteria",
        "use_cases",
        "risk_register",
        "compliance_matrix",
        "traceability_matrix",
        "sdlc_report",
        "open_issues",
    }
    for _, title, sections in payloads:
        pdf = render_artifact_pdf(title, 2, sections)
        assert pdf.startswith(b"%PDF-")
        document = PdfReader(BytesIO(pdf))
        assert title in document.pages[0].extract_text()
        assert "Version 2" in document.pages[0].extract_text()


def test_ieee_srs_groups_requirements_and_renders_a_linked_contents_page() -> None:
    project, requirement = inputs()
    project.summary = (
        "Applicants can submit a personal loan application online. There is one planned release."
    )
    performance = Requirement(
        requirement_code="REQ-008",
        statement="The system must display the eligibility result within 30 seconds.",
        source_stakeholder="Loan Operations Manager",
        categories=[],
        acceptance_criteria=["Result appears within 30 seconds of submission"],
        assumptions=[],
        dependencies=[],
    )
    _, title, sections = build_artifact_payloads(project, [requirement, performance], [], [], None)[
        0
    ]
    by_heading = {section["heading"]: section["content"] for section in sections}
    assert by_heading["1.2 Scope"] == "Applicants can submit a personal loan application online."
    assert by_heading["3.3 Performance Requirements"][0]["requirement_id"] == "REQ-008"
    assert by_heading["3.6 Software System Quality Attributes"][0]["requirement_id"] == "REQ-007"
    assert by_heading["3.1 External Interfaces"] == "Not specified in the current project records."
    assert by_heading["Index"][1]["section"] == "3.3 Performance Requirements"
    reader = PdfReader(BytesIO(render_artifact_pdf(title, 1, sections)))
    assert "Table of Contents" in reader.pages[0].extract_text()
    assert "Appendix B. Requirements Traceability" in reader.pages[0].extract_text()
    assert reader.pages[0].get("/Annots")
    assert "Result appears within 30 seconds of submission" in "".join(
        page.extract_text() for page in reader.pages[1:]
    )


def test_traceability_preserves_requirement_id_and_source() -> None:
    project, requirement = inputs()
    payloads = build_artifact_payloads(project, [requirement], [], [], None)
    trace = next(item for item in payloads if item[0] == "traceability_matrix")
    row = cast(dict[str, Any], trace[2][0]["content"])[0] if False else trace[2][0]["content"][0]
    assert row["requirement_id"] == "REQ-007"
    assert row["source"] == "Compliance Officer"


def test_pdf_renderer_preserves_literal_text_and_continues_across_pages() -> None:
    sections = [
        {"heading": "Scope", "content": "<script>alert(1)</script> & policy notes"},
        {"heading": "Requirements", "content": [f"REQ-{index:03d}" for index in range(120)]},
    ]
    document = PdfReader(BytesIO(render_artifact_pdf("SRS", 1, sections)))
    assert len(document.pages) > 1
    assert "<script>alert(1)</script> & policy notes" in document.pages[0].extract_text()
    assert "REQ-119" in document.pages[-1].extract_text()


def test_compliance_and_risk_outputs_use_requirement_codes() -> None:
    project, requirement = inputs()
    compliance = cast(
        Any,
        SimpleNamespace(
            id="mapping-1",
            requirement_id=requirement.id,
            obligation="Capture consent",
            citations=[{"filename": "policy.txt"}],
        ),
    )
    risk = cast(
        Any,
        SimpleNamespace(
            requirement_id=requirement.id,
            risk_code="RSK-001",
            score=15,
            mitigation="Encrypt evidence",
        ),
    )
    payloads = build_artifact_payloads(project, [requirement], [risk], [compliance], None)
    compliance_matrix = next(item for item in payloads if item[0] == "compliance_matrix")
    risk_register = next(item for item in payloads if item[0] == "risk_register")
    assert compliance_matrix[2][0]["content"][0]["requirement_id"] == "REQ-007"
    assert risk_register[2][0]["content"][0]["requirement_id"] == "REQ-007"
