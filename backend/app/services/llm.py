import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Protocol, TypeVar

import httpx
from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types
from openai import AsyncOpenAI
from pydantic import BaseModel, ValidationError

from app.core.config import Settings, get_settings
from app.schemas.requirement import RequirementCandidate, RequirementExtractionOutput

logger = logging.getLogger(__name__)

StructuredModel = TypeVar("StructuredModel", bound=BaseModel)
TRANSIENT_PROVIDER_STATUS_CODES = {408, 429}


class LLMServiceError(RuntimeError):
    """Safe application-facing error raised by an LLM service."""


class LLMResponseError(LLMServiceError):
    """The provider responded, but its structured output was invalid."""


class LLMProviderError(LLMServiceError):
    """A provider request failed before a valid response was available."""

    def __init__(self, message: str, *, transient: bool) -> None:
        super().__init__(message)
        self.transient = transient


class AsyncHTTPClient(Protocol):
    async def post(self, url: str, *, json: dict[str, Any]) -> httpx.Response: ...


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


def _serialize_user_input(user_input: str | dict[str, Any]) -> str:
    if isinstance(user_input, str):
        return user_input
    return json.dumps(user_input, default=str, ensure_ascii=False)


def _is_transient_provider_status(status_code: int) -> bool:
    return status_code in TRANSIENT_PROVIDER_STATUS_CODES or status_code >= 500


class OpenAILLMService(LLMService):
    def __init__(self, api_key: str, model: str, *, client: Any | None = None) -> None:
        self.client = client if client is not None else AsyncOpenAI(api_key=api_key)
        self.model = model

    async def structured_generate(
        self,
        *,
        system_prompt: str,
        user_input: str | dict[str, Any],
        response_model: type[StructuredModel],
    ) -> StructuredModel:
        logger.info("LLM request provider=openai model=%s", self.model)
        try:
            completion = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": _serialize_user_input(user_input)},
                ],
                response_format=response_model,
            )
            parsed = completion.choices[0].message.parsed
            if parsed is None:
                raise LLMResponseError("The model returned no structured output.")
            return parsed
        except (ValidationError, IndexError, ValueError) as exc:
            raise LLMResponseError("The model returned malformed structured output.") from exc
        except LLMServiceError:
            raise
        except Exception as exc:
            raise LLMServiceError("The language model request failed.") from exc


class GeminiLLMService(LLMService):
    def __init__(self, api_key: str, model: str, *, client: Any | None = None) -> None:
        self.api_key = api_key
        self.client = client
        self.model = model

    async def _generate(
        self,
        *,
        system_prompt: str,
        user_input: str | dict[str, Any],
        response_model: type[StructuredModel],
    ) -> Any:
        contents = _serialize_user_input(user_input)
        config = genai_types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0,
            response_mime_type="application/json",
            response_schema=response_model,
        )
        if self.client is not None:
            return await self.client.models.generate_content(
                model=self.model, contents=contents, config=config
            )
        async with genai.Client(api_key=self.api_key).aio as client:
            return await client.models.generate_content(
                model=self.model, contents=contents, config=config
            )

    async def structured_generate(
        self,
        *,
        system_prompt: str,
        user_input: str | dict[str, Any],
        response_model: type[StructuredModel],
    ) -> StructuredModel:
        logger.info("LLM request provider=gemini model=%s", self.model)
        try:
            response = await self._generate(
                system_prompt=system_prompt,
                user_input=user_input,
                response_model=response_model,
            )
        except genai_errors.APIError as exc:
            code = int(exc.code)
            transient = _is_transient_provider_status(code)
            raise LLMProviderError(
                "The Gemini provider is temporarily unavailable."
                if transient
                else "The Gemini provider request was rejected.",
                transient=transient,
            ) from exc
        except (httpx.TimeoutException, httpx.TransportError, TimeoutError) as exc:
            raise LLMProviderError(
                "The Gemini provider is temporarily unavailable.", transient=True
            ) from exc
        except Exception as exc:
            raise LLMServiceError("The Gemini request failed.") from exc

        try:
            parsed = response.parsed
            if isinstance(parsed, response_model):
                return parsed
            if parsed is not None:
                return response_model.model_validate(parsed)
            if not response.text:
                raise LLMResponseError("The model returned no structured output.")
            return response_model.model_validate_json(response.text)
        except (ValidationError, ValueError, TypeError) as exc:
            raise LLMResponseError("The model returned malformed structured output.") from exc


class OllamaLLMService(LLMService):
    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        client: AsyncHTTPClient | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        self.endpoint = f"{base_url.rstrip('/')}/api/chat"
        self.model = model
        self.client = client
        self.timeout_seconds = timeout_seconds

    async def _post(self, payload: dict[str, Any]) -> httpx.Response:
        if self.client is not None:
            return await self.client.post(self.endpoint, json=payload)
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            return await client.post(self.endpoint, json=payload)

    async def structured_generate(
        self,
        *,
        system_prompt: str,
        user_input: str | dict[str, Any],
        response_model: type[StructuredModel],
    ) -> StructuredModel:
        logger.info("LLM request provider=ollama model=%s", self.model)
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": _serialize_user_input(user_input)},
            ],
            "stream": False,
            "think": False,
            "format": response_model.model_json_schema(),
            "options": {"temperature": 0},
        }
        try:
            response = await self._post(payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            transient = _is_transient_provider_status(status_code)
            raise LLMProviderError(
                "The Ollama provider is temporarily unavailable."
                if transient
                else "The Ollama provider request was rejected.",
                transient=transient,
            ) from exc
        except (httpx.TimeoutException, httpx.TransportError, TimeoutError) as exc:
            raise LLMProviderError(
                "The Ollama provider is temporarily unavailable.", transient=True
            ) from exc
        except Exception as exc:
            raise LLMServiceError("The Ollama request failed.") from exc

        try:
            body = response.json()
            content = body["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Missing assistant content")
            return response_model.model_validate_json(content)
        except (KeyError, TypeError, ValueError, ValidationError) as exc:
            raise LLMResponseError("The model returned malformed structured output.") from exc


class HybridLLMService(LLMService):
    def __init__(self, primary: LLMService, fallback: LLMService) -> None:
        self.primary = primary
        self.fallback = fallback

    async def structured_generate(
        self,
        *,
        system_prompt: str,
        user_input: str | dict[str, Any],
        response_model: type[StructuredModel],
    ) -> StructuredModel:
        try:
            return await self.primary.structured_generate(
                system_prompt=system_prompt,
                user_input=user_input,
                response_model=response_model,
            )
        except LLMProviderError as exc:
            if not exc.transient:
                raise
            logger.warning("LLM provider fallback primary=gemini fallback=ollama")
            return await self.fallback.structured_generate(
                system_prompt=system_prompt,
                user_input=user_input,
                response_model=response_model,
            )


class DeterministicLLMService(LLMService):
    @staticmethod
    def _normalize_statement(text: str) -> str:
        lowered = text.lower()
        for prefix in ("the system shall ", "the system must ", "the system should "):
            if lowered.startswith(prefix):
                return text[len(prefix) :]
        for prefix in ("customers should be able to ", "customers must be able to "):
            if lowered.startswith(prefix):
                return "allow customers to " + text[len(prefix) :]
        actor_capability = re.fullmatch(r"(.+?) can (.+)", text, flags=re.IGNORECASE)
        if actor_capability:
            actor, capability = actor_capability.groups()
            return f"allow {actor.lower()} to {capability}"
        universal_obligation = re.fullmatch(r"every (.+?) must (.+)", text, flags=re.IGNORECASE)
        if universal_obligation:
            subject, obligation = universal_obligation.groups()
            return f"ensure every {subject.lower()} {obligation}"
        universal_requirement = re.fullmatch(
            r"every (.+?) requires (.+)", text, flags=re.IGNORECASE
        )
        if universal_requirement:
            subject, requirement = universal_requirement.groups()
            return f"require {requirement} for every {subject.lower()}"
        need_statement = re.fullmatch(r"(.+?) need(?:s)? (.+)", text, flags=re.IGNORECASE)
        if need_statement:
            subject, requirement = need_statement.groups()
            return f"require {requirement} for {subject.lower()}"
        return text[0].lower() + text[1:]

    async def structured_generate(
        self,
        *,
        system_prompt: str,
        user_input: str | dict[str, Any],
        response_model: type[StructuredModel],
    ) -> StructuredModel:
        del system_prompt
        logger.info("LLM request provider=mock model=deterministic")
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
        lowered_text = self._normalize_statement(text)
        candidate = RequirementCandidate(
            statement=f"The system shall {lowered_text}.",
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


def get_llm_service(settings: Settings | None = None) -> LLMService:
    configured = settings or get_settings()
    if configured.llm_mode == "mock":
        return DeterministicLLMService()
    if configured.llm_mode == "openai":
        if not configured.openai_api_key:
            raise LLMServiceError("OpenAI configuration is incomplete.")
        return OpenAILLMService(configured.openai_api_key, configured.llm_model)
    if configured.llm_mode == "gemini":
        if not configured.gemini_api_key:
            raise LLMServiceError("Gemini configuration is incomplete.")
        return GeminiLLMService(configured.gemini_api_key, configured.gemini_model)
    if configured.llm_mode == "ollama":
        return OllamaLLMService(configured.ollama_base_url, configured.ollama_model)
    if configured.llm_mode == "hybrid":
        if not configured.gemini_api_key:
            raise LLMServiceError("Gemini configuration is incomplete for hybrid mode.")
        return HybridLLMService(
            GeminiLLMService(configured.gemini_api_key, configured.gemini_model),
            OllamaLLMService(configured.ollama_base_url, configured.ollama_model),
        )
    raise LLMServiceError("Unsupported LLM mode.")
