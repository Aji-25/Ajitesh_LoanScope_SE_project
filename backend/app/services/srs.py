import re
from collections.abc import Sequence
from typing import Any

from app.models.database import KnowledgeDocument, Project, Requirement, Stakeholder

NOT_SPECIFIED = "Not specified in the current project records."
REQUIREMENT_SECTIONS = (
    "3.1 External Interfaces",
    "3.2 Functions",
    "3.3 Performance Requirements",
    "3.4 Logical Database Requirements",
    "3.5 Design Constraints",
    "3.6 Software System Quality Attributes",
)
SECTION_CATEGORIES: tuple[set[str], ...] = (
    {"interface", "external interface", "integration", "interoperability", "user interface"},
    set(),
    {"performance", "latency", "throughput", "capacity", "response time"},
    {"logical database", "database", "data model", "data retention", "data integrity"},
    {"constraint", "design constraint", "regulatory constraint", "platform constraint"},
    {
        "security",
        "privacy",
        "data privacy",
        "reliability",
        "availability",
        "usability",
        "maintainability",
        "portability",
        "quality attribute",
        "non functional",
    },
)
RESPONSE_TARGET = re.compile(
    r"\b(?:respond|return|display|deliver|show|complete)\w*\b.{0,100}"
    r"\b(?:within|in less than|in at most)\s+\d+(?:\.\d+)?\s*"
    r"(?:ms|milliseconds?|seconds?|minutes?|hours?)\b",
    re.I,
)
DELIVERY_PLANNING = re.compile(
    r"\b(?:requirements? (?:have|has) been agreed|delivery (?:plan|schedule|team)|"
    r"development (?:budget|schedule|team|method)|team (?:has|have) (?:built|shipped)|"
    r"planned (?:releases?|reviews?|sprints?)|technical risk|scheduled reviews?|"
    r"requirements? (?:are|is) frozen|changes are exceptional|"
    r"before (?:launch|go-live))\b",
    re.I,
)


def requirement_section(requirement: Requirement) -> str:
    categories = {
        " ".join(re.split(r"[-_\s]+", category.lower().strip()))
        for category in requirement.categories
    }
    for index in (0, 2, 3, 4, 5):
        if categories & SECTION_CATEGORIES[index]:
            return REQUIREMENT_SECTIONS[index]
    if RESPONSE_TARGET.search(requirement.statement):
        return REQUIREMENT_SECTIONS[2]
    return REQUIREMENT_SECTIONS[1]


def build_srs_sections(
    project: Project,
    requirements: Sequence[Requirement],
    documents: Sequence[KnowledgeDocument],
    stakeholders: Sequence[Stakeholder],
    issues: list[dict[str, Any]],
    traceability: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {heading: [] for heading in REQUIREMENT_SECTIONS}
    index = []
    for requirement in sorted(requirements, key=lambda item: item.requirement_code):
        heading = requirement_section(requirement)
        row: dict[str, Any] = {
            "requirement_id": requirement.requirement_code,
            "statement": requirement.statement,
            "source": requirement.source_stakeholder,
        }
        if requirement.priority:
            row["priority"] = requirement.priority
        if requirement.acceptance_criteria:
            row["acceptance_criteria"] = requirement.acceptance_criteria
        grouped[heading].append(row)
        index.append({"requirement_id": requirement.requirement_code, "section": heading})

    scope = " ".join(
        sentence
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", project.summary.strip())
        if sentence and not DELIVERY_PLANNING.search(sentence)
    )
    functions = grouped[REQUIREMENT_SECTIONS[1]]
    constraints = grouped[REQUIREMENT_SECTIONS[4]]
    section_rows = [
        ("1. Introduction", 0, None),
        (
            "1.1 Purpose",
            1,
            f"This specification records the software requirements for "
            f"{project.name} for stakeholder, development, and test review.",
        ),
        (
            "1.2 Scope",
            1,
            scope or f"Product category: {project.product_type}. See Section 3 for requirements.",
        ),
        (
            "1.3 Definitions, Acronyms, and Abbreviations",
            1,
            {
                "SRS": "Software Requirements Specification",
                "REQ": "Identifier for a saved project requirement",
                "RSK": "Identifier for a recorded project risk",
            },
        ),
        (
            "1.4 References",
            1,
            [
                "IEEE Std 830-1998, Recommended Practice for Software Requirements Specifications "
                "(document structure).",
                *[
                    f"{document.filename}, version {document.version} ({document.jurisdiction})"
                    for document in documents
                ],
            ],
        ),
        (
            "1.5 Overview",
            1,
            "Section 2 provides the project context. Section 3 contains the "
            "numbered requirements. The appendices and index support review.",
        ),
        ("2. Overall Description", 0, None),
        (
            "2.1 Product Perspective",
            1,
            {
                "product": project.name,
                "product_type": project.product_type,
                "operational_context": "See the project scope in Section 1.2.",
            },
        ),
        (
            "2.2 Product Functions",
            1,
            (
                "See Section 3.2 for the saved product functions ("
                + ", ".join(row["requirement_id"] for row in functions)
                + ")."
            )
            if functions
            else NOT_SPECIFIED,
        ),
        (
            "2.3 User Characteristics",
            1,
            {
                "recorded_stakeholder_roles": list(
                    dict.fromkeys(item.role for item in stakeholders)
                ),
                "end_user_skills": NOT_SPECIFIED,
            },
        ),
        (
            "2.4 Constraints",
            1,
            {
                "project_jurisdiction": project.jurisdiction,
                "recorded_design_constraints": ", ".join(
                    row["requirement_id"] for row in constraints
                )
                or NOT_SPECIFIED,
            },
        ),
        (
            "2.5 Assumptions and Dependencies",
            1,
            {
                "assumptions": list(
                    dict.fromkeys(
                        assumption
                        for requirement in requirements
                        for assumption in requirement.assumptions
                    )
                )
                or NOT_SPECIFIED,
                "dependencies": list(
                    dict.fromkeys(
                        dependency
                        for requirement in requirements
                        for dependency in requirement.dependencies
                    )
                )
                or NOT_SPECIFIED,
            },
        ),
        ("3. Specific Requirements", 0, None),
        *[(heading, 1, rows or NOT_SPECIFIED) for heading, rows in grouped.items()],
        ("3.7 Object-Oriented Models", 1, NOT_SPECIFIED),
        ("Appendix A. Open Requirements Issues", 0, issues or "No wording issues recorded."),
        ("Appendix B. Requirements Traceability", 0, traceability or NOT_SPECIFIED),
        ("Index", 0, index or NOT_SPECIFIED),
    ]
    sections = [
        {"heading": heading, "level": level, "content": content}
        for heading, level, content in section_rows
    ]
    sections[0]["subtitle"] = project.name
    return sections
