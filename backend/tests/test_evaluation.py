from app.services.evaluation import EvaluationCounts, calculate_metrics


def test_evaluation_metrics_use_requirement_and_document_coverage() -> None:
    assert calculate_metrics(EvaluationCounts(10, 8, 6, 7, 9)) == {
        "requirement_completeness": 80.0,
        "evidence_grounding": 60.0,
        "risk_coverage": 70.0,
        "artifact_coverage": 100.0,
    }


def test_empty_project_metrics_are_zero_not_division_error() -> None:
    metrics = calculate_metrics(EvaluationCounts(0, 0, 0, 0, 0))
    assert all(value == 0 for value in metrics.values())
