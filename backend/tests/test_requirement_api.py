import uuid
from typing import Any, cast

import pytest
from fastapi import HTTPException

from app.api.requirements import capture_message
from app.schemas.requirement import RequirementExtractionInput


async def test_capture_message_rejects_mismatched_project_id() -> None:
    path_project_id = uuid.uuid4()
    with pytest.raises(HTTPException) as raised:
        await capture_message(
            project_id=path_project_id,
            data=RequirementExtractionInput(
                project_id=uuid.uuid4(),
                stakeholder_text="Applicants can submit a complete loan application online.",
                source_stakeholder="Operations",
            ),
            user=cast(Any, None),
            session=cast(Any, None),
        )

    assert raised.value.status_code == 422
    assert raised.value.detail == (
        "The body project_id must match the project in the request path."
    )
