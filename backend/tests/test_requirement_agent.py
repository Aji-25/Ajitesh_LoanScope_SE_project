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
