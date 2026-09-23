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
