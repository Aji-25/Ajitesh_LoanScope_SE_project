import uuid
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock

from langgraph.types import Command

from app.api.workflows import latest_workflow
from app.workflows.requirements import build_requirement_graph, initial_state


async def test_graph_routes_clear_requirements_to_completion() -> None:
    graph = build_requirement_graph()
    result = await graph.ainvoke(
        initial_state(
            "project-1", ["REQ-1"], ["The system shall return a decision within 30 seconds."]
        ),
        {"configurable": {"thread_id": "clear"}},
    )
    assert result["status"] == "complete"
    assert result["clarification_questions"] == []


async def test_graph_routes_ambiguity_to_human_review_without_looping() -> None:
    graph = build_requirement_graph()
    state = initial_state("project-1", ["REQ-1"], ["The decision must be returned quickly."])
    state["max_iterations"] = 1
    result = await graph.ainvoke(state, {"configurable": {"thread_id": "ambiguous"}})
    assert result["status"] == "needs_human_review"
    assert result["iteration"] == 1
    assert len(result["clarification_questions"]) == 1


async def test_graph_interrupts_and_resumes_with_clarified_statement() -> None:
    graph = build_requirement_graph()
    config = {"configurable": {"thread_id": "clarification-resume"}}
    state = initial_state("project-1", ["REQ-1"], ["The decision must be returned quickly."])
    interrupted = await graph.ainvoke(state, config)
    assert interrupted["__interrupt__"]

    resumed = await graph.ainvoke(
        Command(
            resume={
                "clarifications": [
                    "The initial eligibility decision must be returned within 30 seconds."
                ]
            }
        ),
        config,
    )
    assert resumed["status"] == "complete"
    assert resumed["iteration"] == 2
    assert resumed["clarification_questions"] == []


async def test_latest_workflow_returns_null_before_first_run() -> None:
    session = SimpleNamespace(scalar=AsyncMock(return_value=None))

    result = await latest_workflow(
        project_id=uuid.uuid4(),
        user=cast(Any, SimpleNamespace(id=uuid.uuid4())),
        session=cast(Any, session),
    )

    assert result is None
