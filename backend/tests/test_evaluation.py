from app.services.evaluation import EvaluationCounts, calculate_metrics


def test_evaluation_metrics_cover_quality_dimensions() -> None:
    metrics = calculate_metrics(
        EvaluationCounts(
            requirements=10,
            complete_requirements=8,
            compliance_mappings=8,
            grounded_mappings=6,
            risks=7,
            approvals=5,
            approved=5,
            artifacts=9,
        )
    )
    assert metrics == {
        "requirement_completeness": 80.0,
        "evidence_grounding": 75.0,
        "risk_coverage": 70.0,
        "approval_progress": 100.0,
        "artifact_coverage": 100.0,
    }


def test_empty_project_metrics_are_zero_not_division_error() -> None:
    metrics = calculate_metrics(EvaluationCounts(0, 0, 0, 0, 0, 0, 0, 0))
    assert all(value == 0 for value in metrics.values())
