import pytest

from app.schemas.sdlc import ProjectCharacteristics
from app.services.sdlc import FACTORS, MODEL_PROFILES, SCORING_VERSION, score_sdlc


@pytest.mark.parametrize("model,profile", MODEL_PROFILES.items())
def test_each_allowed_model_can_win(model: str, profile: tuple[int, ...]) -> None:
    characteristics = ProjectCharacteristics(**dict(zip(FACTORS, profile, strict=True)))
    result = score_sdlc(characteristics)
    assert result.recommendation == model
    assert result.scores[model] == 100
    assert set(result.scores) == set(MODEL_PROFILES)
    assert result.scoring_version == SCORING_VERSION


def test_scores_are_repeatable_and_bounded() -> None:
    inputs = ProjectCharacteristics(
        requirements_volatility=3,
        compliance_criticality=4,
        technical_risk=5,
        customer_collaboration=3,
        release_frequency=2,
        team_experience=4,
    )
    first = score_sdlc(inputs)
    assert first == score_sdlc(inputs)
    assert all(0 <= score <= 100 for score in first.scores.values())
