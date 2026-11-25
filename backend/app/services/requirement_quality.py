import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.database import Requirement


@dataclass(frozen=True)
class QualityFinding:
    kind: str
    message: str
    question: str

    def as_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "message": self.message, "question": self.question}


def analyze_statement(statement: str) -> list[QualityFinding]:
    lowered = statement.lower()
    findings: list[QualityFinding] = []
    questions = {
        "quickly": "How fast should this happen, and when does timing start?",
        "minimal delay": "What is the maximum acceptable delay?",
        "securely": "What specific security control is required?",
        "user friendly": "What should a user be able to do, and how will we judge ease of use?",
        "appropriate": "What rule decides which behavior is appropriate?",
        "high value": "What amount counts as high value?",
    }
    for term, question in questions.items():
        if re.search(rf"\b{term}\b", lowered):
            findings.append(
                QualityFinding("ambiguity", f"The wording {term!r} is unclear.", question)
            )

    if re.search(
        r"\b(?:above|below|over|under|exceeds?)\s+(?:the\s+)?"
        r"(?:(?:configured|specified|approved|defined)\s+)?(?:threshold|limit|amount)\b",
        lowered,
    ):
        findings.append(
            QualityFinding(
                "incomplete",
                "This rule refers to a threshold without specifying its value.",
                "What value or policy reference defines the threshold?",
            )
        )
    return findings


def detect_conflicts(
    statements: list[str], codes: list[str] | None = None
) -> dict[int, list[QualityFinding]]:
    findings: dict[int, list[QualityFinding]] = {}
    for left_index, left in enumerate(statements):
        for right_index, right in enumerate(statements[left_index + 1 :], start=left_index + 1):
            left_text, right_text = left.lower(), right.lower()
            left_words, right_words = set(left_text.split()), set(right_text.split())
            opposite = ("must not" in left_text) != ("must not" in right_text)
            contradicts = opposite and "must" in left_words & right_words and (
                len(left_words & right_words) >= 3
            )
            automatic, manual = (
                (left_text, right_text) if "automatically" in left_text else (right_text, left_text)
            )
            manual_conflict = (
                all(word in automatic for word in ("application", "decision", "automatically"))
                and not re.search(r"\b(?:except|excluding|unless|initial)\b", automatic)
                and all(word in manual for word in ("application", "manual"))
                and ("approval" in manual or "underwriting" in manual)
            )
            if contradicts or manual_conflict:
                kind = "conflict"
                message = "This requirement may conflict with {other}."
                question = "Which rule takes precedence, or when does each apply?"
            else:
                normalized_left = re.sub(r"[^a-z0-9 ]", "", left_text)
                normalized_right = re.sub(r"[^a-z0-9 ]", "", right_text)
                if (
                    re.findall(r"\d+", normalized_left) != re.findall(r"\d+", normalized_right)
                    or SequenceMatcher(None, normalized_left, normalized_right).ratio() < 0.82
                ):
                    continue
                kind = "duplicate"
                message = "This requirement is substantially similar to {other}."
                question = "Should these requirements be combined?"

            for index, other_index in ((left_index, right_index), (right_index, left_index)):
                other = codes[other_index] if codes else "another requirement"
                findings.setdefault(index, []).append(
                    QualityFinding(kind, message.format(other=other), question)
                )
    return findings


def review_requirements(requirements: list["Requirement"]) -> list[list[QualityFinding]]:
    related_findings = detect_conflicts(
        [item.statement for item in requirements], [item.requirement_code for item in requirements]
    )
    return [
        analyze_statement(item.statement) + related_findings.get(index, [])
        for index, item in enumerate(requirements)
    ]


def apply_quality_checks(requirements: list["Requirement"]) -> None:
    for item, findings in zip(requirements, review_requirements(requirements), strict=True):
        previously_flagged = item.clarification_status in {"required", "resolved"}
        item.quality_findings = [finding.as_dict() for finding in findings]
        if findings:
            item.clarification_status = "required"
        elif previously_flagged:
            item.clarification_status = "resolved"
        else:
            item.clarification_status = "not_required"
