from app.services.requirement_quality import analyze_statement, detect_conflicts


def test_quality_analysis_flags_vague_language_without_requiring_criteria() -> None:
    findings = analyze_statement("The system must respond quickly and securely.")
    assert [finding.kind for finding in findings] == ["ambiguity", "ambiguity"]


def test_conflict_detection_matches_opposing_requirements() -> None:
    conflicts = detect_conflicts(
        [
            "The system must retain applicant documents after approval",
            "The system must not retain applicant documents after approval",
        ]
    )
    assert set(conflicts) == {0, 1}


def test_quality_analysis_accepts_measurable_complete_requirement() -> None:
    findings = analyze_statement("The system shall return a decision within 30 seconds.")
    assert findings == []


def test_quality_analysis_requests_high_value_threshold() -> None:
    findings = analyze_statement("High value loans require extra approval.")
    assert [finding.kind for finding in findings] == ["ambiguity"]


def test_quality_analysis_checks_threshold_in_the_requirement() -> None:
    assert analyze_statement(
        "Every application above INR 500,000 requires manual underwriting approval."
    ) == []
    findings = analyze_statement("Every application above the threshold requires manual approval.")
    assert [finding.kind for finding in findings] == ["incomplete"]


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
        ],
        ["REQ-001", "REQ-002"],
    )
    assert conflicts[0][0].kind == "conflict"
    assert "REQ-002" in conflicts[0][0].message
    assert "REQ-001" in conflicts[1][0].message


def test_initial_eligibility_does_not_conflict_with_manual_underwriting() -> None:
    assert detect_conflicts(
        [
            "Every application must receive an initial eligibility decision automatically.",
            "Every application above 500000 requires manual underwriting approval.",
        ]
    ) == {}
