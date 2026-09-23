from app.schemas.sdlc import ProjectCharacteristics
from app.services.sdlc import score_sdlc


def test_agile_wins_for_volatile_collaborative_frequent_delivery() -> None:
    result = score_sdlc(
        ProjectCharacteristics(
            requirements_volatility=5,
            compliance_criticality=2,
            technical_risk=2,
            customer_collaboration=5,
            release_frequency=5,
            team_experience=4,
        )
    )
    assert result.recommendation == "agile"


def test_v_model_wins_for_stable_high_assurance_project() -> None:
    result = score_sdlc(
        ProjectCharacteristics(
            requirements_volatility=1,
            compliance_criticality=5,
            technical_risk=5,
            customer_collaboration=2,
            release_frequency=1,
            team_experience=4,
        )
    )
    assert result.recommendation == "v_model"


def test_scores_are_repeatable_and_bounded() -> None:
    inputs = ProjectCharacteristics(
        requirements_volatility=3,
        compliance_criticality=4,
        technical_risk=5,
        customer_collaboration=3,
        release_frequency=2,
        team_experience=4,
    )
    assert score_sdlc(inputs) == score_sdlc(inputs)
    assert all(0 <= score <= 100 for score in score_sdlc(inputs).scores.values())
