import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Project, Requirement, WorkflowRun
from app.schemas.workflow import WorkflowResponse
from app.workflows.checkpoints import postgres_checkpointer
from app.workflows.requirements import build_requirement_graph, initial_state


class WorkflowService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def start(
        self, project_id: uuid.UUID, owner_id: uuid.UUID, max_iterations: int
    ) -> WorkflowResponse | None:
        project = await self.session.scalar(
            select(Project).where(Project.id == project_id, Project.created_by_id == owner_id)
        )
        if project is None:
            return None
        requirements = list(
            await self.session.scalars(
                select(Requirement)
                .where(Requirement.project_id == project_id)
                .order_by(Requirement.requirement_code)
            )
        )
        thread_id = f"requirements-{project_id}-{uuid.uuid4()}"
        state = initial_state(
            str(project_id),
            [str(item.id) for item in requirements],
            [item.statement for item in requirements],
        )
        state["max_iterations"] = max_iterations
        try:
            async with postgres_checkpointer() as saver:
                graph = build_requirement_graph(saver)
                output = await graph.ainvoke(state, {"configurable": {"thread_id": thread_id}})
        except Exception as exc:
            run = WorkflowRun(
                project_id=project_id,
                thread_id=thread_id,
                status="failed",
                current_node="error",
                state_snapshot=state,
                error_message=str(exc)[:1000],
            )
            self.session.add(run)
            await self.session.commit()
            raise
        snapshot = dict(output)
        run = WorkflowRun(
            project_id=project_id,
            thread_id=thread_id,
            status=str(snapshot["status"]),
            current_node="finish",
            state_snapshot=snapshot,
        )
        self.session.add(run)
        await self.session.commit()
        return WorkflowResponse(
            id=run.id,
            thread_id=thread_id,
            status=run.status,
            current_node=run.current_node,
            state=snapshot,
        )

    async def get(self, run_id: uuid.UUID, owner_id: uuid.UUID) -> WorkflowResponse | None:
        run = await self.session.scalar(
            select(WorkflowRun)
            .join(Project)
            .where(WorkflowRun.id == run_id, Project.created_by_id == owner_id)
        )
        if run is None:
            return None
        return WorkflowResponse(
            id=run.id,
            thread_id=run.thread_id,
            status=run.status,
            current_node=run.current_node,
            state=run.state_snapshot,
        )
