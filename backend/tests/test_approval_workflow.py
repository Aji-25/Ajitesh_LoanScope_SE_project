from langgraph.types import Command

from app.workflows.approval import ApprovalState, build_approval_graph


async def test_approval_graph_interrupts_and_resumes() -> None:
    graph = build_approval_graph()
    config = {"configurable": {"thread_id": "approval-test"}}
    state = ApprovalState(
        approval_id="a1",
        title="Approve baseline",
        payload={"count": 3},
        decision=None,
        decision_payload={},
        status="pending",
    )
    interrupted = await graph.ainvoke(state, config)
    assert interrupted["__interrupt__"]
    resumed = await graph.ainvoke(
        Command(resume={"action": "approve", "comment": "Reviewed"}), config
    )
    assert resumed["status"] == "approved"
    assert resumed["decision"] == "approve"


async def test_approval_graph_routes_regeneration() -> None:
    graph = build_approval_graph()
    config = {"configurable": {"thread_id": "regenerate-test"}}
    state = ApprovalState(
        approval_id="a2",
        title="Approve SDLC",
        payload={},
        decision=None,
        decision_payload={},
        status="pending",
    )
    await graph.ainvoke(state, config)
    resumed = await graph.ainvoke(
        Command(resume={"action": "regenerate", "comment": "Adjust inputs"}), config
    )
    assert resumed["status"] == "regenerate"
