from app.services.requirement_quality import analyze_statement, detect_conflicts


def test_quality_analysis_flags_vague_language_and_missing_criteria() -> None:
    findings = analyze_statement("The system must respond quickly and securely.", [])
    assert {finding.kind for finding in findings} == {"ambiguity", "incomplete"}
    assert len(findings) == 3


def test_conflict_detection_matches_opposing_requirements() -> None:
    conflicts = detect_conflicts(
        [
            "The system must retain applicant documents after approval",
            "The system must not retain applicant documents after approval",
        ]
    )
    assert set(conflicts) == {0, 1}


def test_quality_analysis_accepts_measurable_complete_requirement() -> None:
    findings = analyze_statement(
        "The system shall return a decision within 30 seconds.",
        ["The measured response time is at most 30 seconds."],
    )
    assert findings == []


def test_quality_analysis_requests_high_value_threshold() -> None:
    findings = analyze_statement(
        "High value loans require extra approval.", ["Approval is recorded."]
    )
    assert [finding.kind for finding in findings] == ["ambiguity"]


def test_quality_analysis_flags_near_duplicates() -> None:
    conflicts = detect_conflicts(
        [
            "The system shall allow customers to apply for a loan online.",
            "The system shall allow customers to apply for a loan online",
        ]
    )
    assert all(any(item.kind == "duplicate" for item in conflicts[index]) for index in (0, 1))


def test_quality_analysis_flags_manual_exception_to_automatic_decision() -> None:
    conflicts = detect_conflicts(
        [
            "Every loan application must receive a decision automatically.",
            "Every application above 500000 requires manual underwriting approval.",
        ]
    )
    assert all(any(item.kind == "conflict" for item in conflicts[index]) for index in (0, 1))
