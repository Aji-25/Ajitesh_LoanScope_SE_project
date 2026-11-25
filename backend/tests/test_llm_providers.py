from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from google.genai import errors as genai_errors

from app.core.config import Settings
from app.schemas.requirement import RequirementCandidate, RequirementExtractionOutput
from app.services.llm import (
    DeterministicLLMService,
    GeminiLLMService,
    HybridLLMService,
    LLMProviderError,
    LLMResponseError,
    LLMService,
    LLMServiceError,
    OllamaLLMService,
    OpenAILLMService,
    StructuredModel,
    get_llm_service,
)


def requirement_output() -> RequirementExtractionOutput:
    return RequirementExtractionOutput(
        candidates=[
            RequirementCandidate(
                statement="The system shall encrypt identity documents at rest.",
                categories=["security"],
                source="Security reviewer",
                priority="Must",
                assumptions=[],
                acceptance_criteria=["Stored identity documents use approved encryption."],
                confidence=0.93,
            )
        ],
        summary="One security requirement was extracted.",
    )


def settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "database_url": "postgresql+asyncpg://user:password@localhost/database",
        "jwt_secret": "a-secret-that-is-at-least-thirty-two-characters",
        "llm_mode": "mock",
    }
    values.update(overrides)
    return Settings(**values)


class FakeGeminiModels:
    def __init__(self, response: object | None = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.request: dict[str, Any] | None = None

    async def generate_content(self, **kwargs: Any) -> object:
        self.request = kwargs
        if self.error is not None:
            raise self.error
        if self.response is None:
            raise AssertionError("A fake Gemini response is required.")
        return self.response


class FakeGeminiClient:
    def __init__(self, models: FakeGeminiModels) -> None:
        self.models = models


class FakeHTTPClient:
    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        self.url: str | None = None
        self.payload: dict[str, Any] | None = None

    async def post(self, url: str, *, json: dict[str, Any]) -> httpx.Response:
        self.url = url
        self.payload = json
        return self.response


class FakeOpenAICompletions:
    def __init__(self, response: RequirementExtractionOutput) -> None:
        self.response = response
        self.request: dict[str, Any] | None = None

    async def parse(self, **kwargs: Any) -> object:
        self.request = kwargs
        message = SimpleNamespace(parsed=self.response)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeOpenAIClient:
    def __init__(self, completions: FakeOpenAICompletions) -> None:
        self.beta = SimpleNamespace(chat=SimpleNamespace(completions=completions))


class StubLLM(LLMService):
    def __init__(
        self,
        *,
        result: RequirementExtractionOutput | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error
        self.calls = 0

    async def structured_generate(
        self,
        *,
        system_prompt: str,
        user_input: str | dict[str, Any],
        response_model: type[StructuredModel],
    ) -> StructuredModel:
        del system_prompt, user_input
        self.calls += 1
        if self.error is not None:
            raise self.error
        if self.result is None:
            raise AssertionError("A stub result is required.")
        return response_model.model_validate(self.result.model_dump())


async def generate(service: LLMService) -> RequirementExtractionOutput:
    return await service.structured_generate(
        system_prompt="Extract only supported requirements.",
        user_input={
            "stakeholder_text": "Identity documents must be encrypted at rest.",
            "source_stakeholder": "Security reviewer",
        },
        response_model=RequirementExtractionOutput,
    )


def test_provider_configuration_selects_all_supported_modes() -> None:
    assert isinstance(get_llm_service(settings(llm_mode="mock")), DeterministicLLMService)
    assert isinstance(
        get_llm_service(
            settings(llm_mode="openai", openai_api_key="test-key", llm_model="openai-model")
        ),
        OpenAILLMService,
    )

    gemini = get_llm_service(
        settings(llm_mode="gemini", gemini_api_key="test-key", gemini_model="gemini-model")
    )
    assert isinstance(gemini, GeminiLLMService)
    assert gemini.model == "gemini-model"

    ollama = get_llm_service(
        settings(
            llm_mode="ollama",
            ollama_base_url="http://ollama.internal:11434/",
            ollama_model="qwen-test",
        )
    )
    assert isinstance(ollama, OllamaLLMService)
    assert ollama.endpoint == "http://ollama.internal:11434/api/chat"
    assert ollama.model == "qwen-test"

    hybrid = get_llm_service(
        settings(
            llm_mode="hybrid",
            gemini_api_key="test-key",
            gemini_model="gemini-model",
            ollama_model="qwen-test",
        )
    )
    assert isinstance(hybrid, HybridLLMService)
    assert isinstance(hybrid.primary, GeminiLLMService)
    assert isinstance(hybrid.fallback, OllamaLLMService)


@pytest.mark.parametrize(
    ("mode", "message"),
    [
        ("openai", "OpenAI configuration is incomplete"),
        ("gemini", "Gemini configuration is incomplete"),
        ("hybrid", "Gemini configuration is incomplete for hybrid mode"),
    ],
)
def test_provider_configuration_rejects_missing_credentials(mode: str, message: str) -> None:
    with pytest.raises(LLMServiceError, match=message):
        get_llm_service(settings(llm_mode=mode, openai_api_key=None, gemini_api_key=None))


async def test_gemini_returns_validated_structured_output() -> None:
    expected = requirement_output()
    models = FakeGeminiModels(response=SimpleNamespace(parsed=expected.model_dump(), text=None))
    service = GeminiLLMService("test-key", "gemini-test", client=FakeGeminiClient(models))

    result = await generate(service)

    assert result == expected
    assert models.request is not None
    assert models.request["model"] == "gemini-test"
    assert models.request["config"].response_schema is RequirementExtractionOutput


async def test_openai_existing_structured_output_path_still_works() -> None:
    expected = requirement_output()
    completions = FakeOpenAICompletions(expected)
    service = OpenAILLMService("test-key", "openai-test", client=FakeOpenAIClient(completions))

    result = await generate(service)

    assert result == expected
    assert completions.request is not None
    assert completions.request["model"] == "openai-test"
    assert completions.request["response_format"] is RequirementExtractionOutput


async def test_provider_logging_identifies_provider_and_model_without_credentials(
    caplog: pytest.LogCaptureFixture,
) -> None:
    expected = requirement_output()
    models = FakeGeminiModels(response=SimpleNamespace(parsed=expected, text=None))
    service = GeminiLLMService(
        "private-test-credential", "gemini-test", client=FakeGeminiClient(models)
    )

    with caplog.at_level("INFO"):
        await generate(service)

    assert "provider=gemini model=gemini-test" in caplog.text
    assert "private-test-credential" not in caplog.text


async def test_ollama_posts_schema_and_returns_validated_output() -> None:
    expected = requirement_output()
    response = httpx.Response(
        200,
        request=httpx.Request("POST", "http://ollama:11434/api/chat"),
        json={"message": {"role": "assistant", "content": expected.model_dump_json()}},
    )
    client = FakeHTTPClient(response)
    service = OllamaLLMService("http://ollama:11434", "qwen3:4b", client=client)

    result = await generate(service)

    assert result == expected
    assert client.url == "http://ollama:11434/api/chat"
    assert client.payload is not None
    assert client.payload["model"] == "qwen3:4b"
    assert client.payload["stream"] is False
    assert client.payload["think"] is False
    assert client.payload["format"] == RequirementExtractionOutput.model_json_schema()


async def test_hybrid_falls_back_after_transient_provider_failure() -> None:
    primary = StubLLM(error=LLMProviderError("Gemini rate limit reached.", transient=True))
    fallback = StubLLM(result=requirement_output())

    result = await generate(HybridLLMService(primary, fallback))

    assert result == requirement_output()
    assert primary.calls == 1
    assert fallback.calls == 1


async def test_hybrid_returns_primary_success_without_calling_fallback() -> None:
    primary = StubLLM(result=requirement_output())
    fallback = StubLLM(result=requirement_output())

    result = await generate(HybridLLMService(primary, fallback))

    assert result == requirement_output()
    assert primary.calls == 1
    assert fallback.calls == 0


async def test_hybrid_falls_back_when_gemini_returns_transient_service_error() -> None:
    models = FakeGeminiModels(
        error=genai_errors.ServerError(503, {"error": {"message": "Unavailable"}})
    )
    primary = GeminiLLMService("test-key", "gemini-test", client=FakeGeminiClient(models))
    fallback = StubLLM(result=requirement_output())

    result = await generate(HybridLLMService(primary, fallback))

    assert result == requirement_output()
    assert fallback.calls == 1


@pytest.mark.parametrize(
    "error",
    [
        LLMProviderError("Gemini credentials were rejected.", transient=False),
        LLMResponseError("The model returned malformed structured output."),
        RuntimeError("Internal application state is invalid."),
    ],
)
async def test_hybrid_does_not_fall_back_for_non_transient_or_application_failures(
    error: Exception,
) -> None:
    primary = StubLLM(error=error)
    fallback = StubLLM(result=requirement_output())

    with pytest.raises(type(error)):
        await generate(HybridLLMService(primary, fallback))

    assert primary.calls == 1
    assert fallback.calls == 0


async def test_gemini_malformed_response_fails_safely() -> None:
    models = FakeGeminiModels(response=SimpleNamespace(parsed=None, text='{"candidates": []}'))
    service = GeminiLLMService("test-key", "gemini-test", client=FakeGeminiClient(models))

    with pytest.raises(LLMResponseError, match="malformed"):
        await generate(service)


async def test_ollama_malformed_response_fails_safely() -> None:
    response = httpx.Response(
        200,
        request=httpx.Request("POST", "http://ollama:11434/api/chat"),
        json={"message": {"role": "assistant", "content": "not-json"}},
    )
    service = OllamaLLMService("http://ollama:11434", "qwen3:4b", client=FakeHTTPClient(response))

    with pytest.raises(LLMResponseError, match="malformed"):
        await generate(service)


async def test_gemini_timeout_is_classified_as_transient_provider_failure() -> None:
    models = FakeGeminiModels(error=httpx.ReadTimeout("Gemini timed out."))
    service = GeminiLLMService("test-key", "gemini-test", client=FakeGeminiClient(models))

    with pytest.raises(LLMProviderError) as error:
        await generate(service)

    assert error.value.transient is True
