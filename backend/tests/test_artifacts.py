from types import SimpleNamespace
from typing import Any, cast

from app.models.database import Project, Requirement
from app.services.artifacts import build_artifact_payloads, render_html


def inputs() -> tuple[Project, Requirement]:
    project = cast(Project, SimpleNamespace(summary="Digital personal loan origination"))
    requirement = cast(
        Requirement,
        SimpleNamespace(
            id="id-1",
            requirement_code="REQ-007",
            statement="The system shall capture consent.",
            source_stakeholder="Compliance Officer",
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


def test_traceability_preserves_requirement_id_and_source() -> None:
    project, requirement = inputs()
    payloads = build_artifact_payloads(project, [requirement], [], [], None)
    trace = next(item for item in payloads if item[0] == "traceability_matrix")
    row = cast(dict[str, Any], trace[2][0]["content"])[0] if False else trace[2][0]["content"][0]
    assert row["requirement_id"] == "REQ-007"
    assert row["source"] == "Compliance Officer"


def test_html_renderer_escapes_source_content() -> None:
    output = render_html("SRS", [{"heading": "Scope", "content": "<script>alert(1)</script>"}])
    assert "<script>" not in output
    assert "&lt;script&gt;" in output
