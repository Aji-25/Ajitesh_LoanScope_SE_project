from typing import Any, Literal, TypedDict

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class RequirementWorkflowState(TypedDict):
    project_id: str
    requirement_ids: list[str]
    statements: list[str]
    quality_findings: list[str]
    clarification_questions: list[str]
    iteration: int
    max_iterations: int
    status: str
    error: str | None


def normalize_node(state: RequirementWorkflowState) -> dict[str, object]:
    statements = [" ".join(statement.split()) for statement in state["statements"]]
    return {"statements": statements, "iteration": state["iteration"] + 1, "status": "reviewing"}


def quality_node(state: RequirementWorkflowState) -> dict[str, object]:
    vague_terms = ("quickly", "securely", "user friendly", "minimal delay")
    findings: list[str] = []
    questions: list[str] = []
    for statement in state["statements"]:
        present = [term for term in vague_terms if term in statement.lower()]
        if present:
            findings.append(f"Ambiguous language: {', '.join(present)}")
            questions.append(f"What measurable target should replace {present[0]!r}?")
    return {
        "quality_findings": findings,
        "clarification_questions": questions,
        "status": "clarification_needed" if questions else "validated",
    }


def route_after_quality(state: RequirementWorkflowState) -> Literal["clarify", "finish"]:
    if state["clarification_questions"] and state["iteration"] < state["max_iterations"]:
        return "clarify"
    return "finish"


def clarification_node(state: RequirementWorkflowState) -> dict[str, object]:
    return {"status": "awaiting_clarification"}


def finish_node(state: RequirementWorkflowState) -> dict[str, object]:
    status = "needs_human_review" if state["clarification_questions"] else "complete"
    return {"status": status}


def build_requirement_graph(checkpointer: BaseCheckpointSaver[Any] | None = None) -> Any:
    graph = StateGraph(RequirementWorkflowState)
    graph.add_node("normalize", normalize_node)
    graph.add_node("quality", quality_node)
    graph.add_node("clarify", clarification_node)
    graph.add_node("finish", finish_node)
    graph.add_edge(START, "normalize")
    graph.add_edge("normalize", "quality")
    graph.add_conditional_edges(
        "quality", route_after_quality, {"clarify": "clarify", "finish": "finish"}
    )
    graph.add_edge("clarify", "finish")
    graph.add_edge("finish", END)
    return graph.compile(checkpointer=checkpointer or InMemorySaver())


def initial_state(
    project_id: str, requirement_ids: list[str], statements: list[str]
) -> RequirementWorkflowState:
    return RequirementWorkflowState(
        project_id=project_id,
        requirement_ids=requirement_ids,
        statements=statements,
        quality_findings=[],
        clarification_questions=[],
        iteration=0,
        max_iterations=2,
        status="started",
        error=None,
    )
