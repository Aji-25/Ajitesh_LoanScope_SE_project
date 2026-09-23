import pytest
from pydantic import ValidationError

from app.schemas.project import ProjectCreate


def test_project_create_normalizes_text() -> None:
    project = ProjectCreate(
        name="  Riverstone lending portal  ",
        summary="  Replace email based document review with a controlled digital workflow.  ",
        jurisdiction="  India  ",
    )

    assert project.name == "Riverstone lending portal"
    assert project.jurisdiction == "India"
    assert project.summary.startswith("Replace email")


def test_project_create_rejects_an_unusable_summary() -> None:
    with pytest.raises(ValidationError):
        ProjectCreate(name="Riverstone", summary="Too brief", jurisdiction="India")
