import pytest
from pydantic import ValidationError

from app.schemas.security import RiskAssessment, review_headline


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Missing encryption for identity documents", "Verify encryption for identity documents"),
        ("PDF Limit not enforced", "Verify PDF Limit"),
        (
            "Manual underwriting approval is not enforced for high-value loans",
            "Verify manual underwriting approval for high-value loans",
        ),
        ("Add consent timestamp", "Add consent timestamp"),
    ],
)
def test_headline_describes_a_check_without_claiming_control_is_absent(
    title: str, expected: str
) -> None:
    assert review_headline(title) == expected


def test_review_rejects_out_of_range_ratings() -> None:
    with pytest.raises(ValidationError):
        RiskAssessment(
            title="Consent record",
            remaining_risk="The consent record may omit the notice version.",
            next_step="Save the notice version with each consent record.",
            likelihood_reason="A standard consent form may omit this information.",
            impact_reason="Reviewers would be unable to verify which notice was accepted.",
            likelihood=6,
            impact=5,
        )
