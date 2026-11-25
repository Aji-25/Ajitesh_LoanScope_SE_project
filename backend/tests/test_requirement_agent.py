import uuid
from typing import Any

import pytest

from app.agents.requirement import RequirementAgent
from app.schemas.requirement import RequirementExtractionInput, RequirementExtractionOutput
from app.services.llm import (
    DeterministicLLMService,
    LLMService,
    LLMServiceError,
    StructuredModel,
)


async def test_requirement_agent_returns_typed_output() -> None:
    result = await RequirementAgent(DeterministicLLMService()).run(
        RequirementExtractionInput(
            project_id=uuid.uuid4(),
            stakeholder_text=(
                "Applicants can upload identity evidence before submitting the application."
            ),
            source_stakeholder="Loan Operations Manager",
        )
    )

    assert isinstance(result, RequirementExtractionOutput)
    assert result.candidates[0].confidence == 0.9
    assert result.candidates[0].source == "Loan Operations Manager"


async def test_requirement_agent_exposes_uncertainty_for_vague_language() -> None:
    result = await RequirementAgent(DeterministicLLMService()).run(
        RequirementExtractionInput(
            project_id=uuid.uuid4(),
            stakeholder_text="The underwriting decision must be returned quickly and securely.",
            source_stakeholder="Credit Risk Lead",
        )
    )

    assert result.candidates[0].clarification_needed is True
    assert "quickly" in (result.candidates[0].uncertainty_reason or "")
    assert result.candidates[0].acceptance_criteria == []


async def test_requirement_agent_normalizes_customer_capability_grammar() -> None:
    result = await RequirementAgent(DeterministicLLMService()).run(
        RequirementExtractionInput(
            project_id=uuid.uuid4(),
            stakeholder_text="Customers should be able to apply for a personal loan online.",
            source_stakeholder="Loan Operations Manager",
        )
    )

    assert result.candidates[0].statement == (
        "The system shall allow customers to apply for a personal loan online."
    )


@pytest.mark.parametrize(
    ("stakeholder_text", "expected"),
    [
        (
            "The system must encrypt KYC documents at rest.",
            "The system shall encrypt KYC documents at rest.",
        ),
        (
            "Applicants can upload identity evidence before submitting the application.",
            "The system shall allow applicants to upload identity evidence before submitting "
            "the application.",
        ),
        (
            "Every loan application must receive an eligibility decision.",
            "The system shall ensure every loan application receive an eligibility decision.",
        ),
        (
            "Every application above ₹500,000 requires manual underwriting approval.",
            "The system shall require manual underwriting approval for every application above "
            "₹500,000.",
        ),
        (
            "High value loans need extra approval.",
            "The system shall require extra approval for high value loans.",
        ),
    ],
)
async def test_requirement_agent_normalizes_common_stakeholder_grammar(
    stakeholder_text: str, expected: str
) -> None:
    result = await RequirementAgent(DeterministicLLMService()).run(
        RequirementExtractionInput(
            project_id=uuid.uuid4(),
            stakeholder_text=stakeholder_text,
            source_stakeholder="Validation Stakeholder",
        )
    )

    assert result.candidates[0].statement == expected


class MalformedLLM(LLMService):
    async def structured_generate(
        self,
        *,
        system_prompt: str,
        user_input: str | dict[str, Any],
        response_model: type[StructuredModel],
    ) -> StructuredModel:
        del system_prompt, user_input, response_model
        raise LLMServiceError("The model returned malformed structured output.")


async def test_requirement_agent_propagates_malformed_output_as_service_error() -> None:
    with pytest.raises(LLMServiceError, match="malformed"):
        await RequirementAgent(MalformedLLM()).run(
            RequirementExtractionInput(
                project_id=uuid.uuid4(),
                stakeholder_text="Applicants can upload identity evidence before submitting.",
                source_stakeholder="Operations",
            )
        )
