from typing import Any, Literal, TypedDict

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class ApprovalState(TypedDict):
    approval_id: str
    title: str
    payload: dict[str, Any]
    decision: str | None
    decision_payload: dict[str, Any]
    status: str


def request_approval(state: ApprovalState) -> dict[str, Any]:
    response = interrupt(
        {
            "approval_id": state["approval_id"],
            "title": state["title"],
            "payload": state["payload"],
            "allowed_actions": ["approve", "reject", "edit", "regenerate"],
        }
    )
    return {"decision": response["action"], "decision_payload": response, "status": "resumed"}


def route_decision(state: ApprovalState) -> Literal["accepted", "revision"]:
    return "accepted" if state["decision"] == "approve" else "revision"


def accepted(state: ApprovalState) -> dict[str, Any]:
    del state
    return {"status": "approved"}


def revision(state: ApprovalState) -> dict[str, Any]:
    return {"status": str(state["decision"])}


def build_approval_graph(checkpointer: BaseCheckpointSaver[Any] | None = None) -> Any:
    graph = StateGraph(ApprovalState)
    graph.add_node("request_approval", request_approval)
    graph.add_node("accepted", accepted)
    graph.add_node("revision", revision)
    graph.add_edge(START, "request_approval")
    graph.add_conditional_edges(
        "request_approval", route_decision, {"accepted": "accepted", "revision": "revision"}
    )
    graph.add_edge("accepted", END)
    graph.add_edge("revision", END)
    return graph.compile(checkpointer=checkpointer or InMemorySaver())
