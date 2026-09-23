from abc import ABC, abstractmethod
from typing import Any, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel, ValidationError

from app.core.config import get_settings
from app.schemas.requirement import RequirementCandidate, RequirementExtractionOutput

StructuredModel = TypeVar("StructuredModel", bound=BaseModel)


class LLMServiceError(RuntimeError):
    pass


class LLMService(ABC):
    @abstractmethod
    async def structured_generate(
        self,
        *,
        system_prompt: str,
        user_input: str | dict[str, Any],
        response_model: type[StructuredModel],
    ) -> StructuredModel:
        raise NotImplementedError


class OpenAILLMService(LLMService):
    def __init__(self, api_key: str, model: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def structured_generate(
        self,
        *,
        system_prompt: str,
        user_input: str | dict[str, Any],
        response_model: type[StructuredModel],
    ) -> StructuredModel:
        try:
            completion = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": str(user_input)},
                ],
                response_format=response_model,
            )
            parsed = completion.choices[0].message.parsed
            if parsed is None:
                raise LLMServiceError("The model returned no structured output.")
            return parsed
        except (ValidationError, IndexError, ValueError) as exc:
            raise LLMServiceError("The model returned malformed structured output.") from exc
        except LLMServiceError:
            raise
        except Exception as exc:
            raise LLMServiceError("The language model request failed.") from exc


class DeterministicLLMService(LLMService):
    async def structured_generate(
        self,
        *,
        system_prompt: str,
        user_input: str | dict[str, Any],
        response_model: type[StructuredModel],
    ) -> StructuredModel:
        del system_prompt
        if response_model is not RequirementExtractionOutput or not isinstance(user_input, dict):
            raise LLMServiceError("No deterministic response is defined for this schema.")

        text = str(user_input["stakeholder_text"]).strip().rstrip(".")
        source = str(user_input["source_stakeholder"])
        lowered = text.lower()
        categories = ["functional"]
        if any(term in lowered for term in ("encrypt", "access", "authenticate", "secure")):
            categories.append("security")
        if any(term in lowered for term in ("within", "seconds", "concurrent", "response time")):
            categories.append("performance")
        if any(term in lowered for term in ("consent", "personal data", "retention", "privacy")):
            categories.append("privacy")
        vague_terms = [
            term
            for term in ("quickly", "secure", "user friendly", "minimal delay")
            if term in lowered
        ]
        candidate = RequirementCandidate(
            statement=f"The system shall {text[0].lower()}{text[1:]}.",
            categories=list(dict.fromkeys(categories)),
            source=source,
            priority="Must",
            assumptions=[],
            acceptance_criteria=(
                [] if vague_terms else [f"A reviewer can verify that {text[0].lower()}{text[1:]}."]
            ),
            confidence=0.62 if vague_terms else 0.9,
            clarification_needed=bool(vague_terms),
            uncertainty_reason=(
                f"The statement contains vague language: {', '.join(vague_terms)}."
                if vague_terms
                else None
            ),
        )
        output = RequirementExtractionOutput(
            candidates=[candidate],
            summary=(
                "One structured requirement candidate was extracted from the stakeholder statement."
            ),
        )
        return response_model.model_validate(output.model_dump())


def get_llm_service() -> LLMService:
    settings = get_settings()
    if settings.llm_mode == "mock":
        return DeterministicLLMService()
    if settings.llm_mode == "openai" and settings.openai_api_key:
        return OpenAILLMService(settings.openai_api_key, settings.llm_model)
    raise LLMServiceError("LLM configuration is incomplete.")
