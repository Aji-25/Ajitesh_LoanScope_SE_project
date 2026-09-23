from app.schemas.requirement import RequirementExtractionInput, RequirementExtractionOutput
from app.services.llm import LLMService

REQUIREMENT_PROMPT = """You are the Requirement Agent for a digital personal loan software project.
Extract only requirements supported by the stakeholder statement.
Classify each requirement, retain its named source, expose assumptions and uncertainty, and never
resolve ambiguity silently. Return the requested structured schema. Do not invent regulations,
stakeholder answers, priorities, acceptance criteria, or project facts that are not supported."""


class RequirementAgent:
    def __init__(self, llm: LLMService) -> None:
        self.llm = llm

    async def run(self, data: RequirementExtractionInput) -> RequirementExtractionOutput:
        return await self.llm.structured_generate(
            system_prompt=REQUIREMENT_PROMPT,
            user_input={
                "project_id": str(data.project_id),
                "stakeholder_text": data.stakeholder_text,
                "source_stakeholder": data.source_stakeholder,
            },
            response_model=RequirementExtractionOutput,
        )
