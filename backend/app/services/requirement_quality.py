from dataclasses import dataclass


@dataclass(frozen=True)
class QualityFinding:
    kind: str
    message: str
    question: str

    def as_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "message": self.message, "question": self.question}


def analyze_statement(statement: str, acceptance_criteria: list[str]) -> list[QualityFinding]:
    lowered = statement.lower()
    findings: list[QualityFinding] = []
    for term in ("quickly", "securely", "user friendly", "minimal delay", "appropriate"):
        if term in lowered:
            findings.append(
                QualityFinding(
                    kind="ambiguity",
                    message=f"The term {term!r} is not measurable.",
                    question=f"What measurable target should replace {term!r}?",
                )
            )
    if not acceptance_criteria:
        findings.append(
            QualityFinding(
                kind="incomplete",
                message="No acceptance criterion is defined.",
                question="How will a reviewer verify this requirement?",
            )
        )
    return findings


def detect_conflicts(statements: list[str]) -> dict[int, list[QualityFinding]]:
    conflicts: dict[int, list[QualityFinding]] = {}
    for left_index, left in enumerate(statements):
        for right_index, right in enumerate(statements[left_index + 1 :], start=left_index + 1):
            left_words = set(left.lower().split())
            right_words = set(right.lower().split())
            overlap = left_words & right_words
            opposite = ("must" in left_words and "must not" in right.lower()) or (
                "must not" in left.lower() and "must" in right_words
            )
            if opposite and len(overlap) >= 3:
                for index in (left_index, right_index):
                    conflicts.setdefault(index, []).append(
                        QualityFinding(
                            kind="conflict",
                            message="This requirement may contradict another baseline statement.",
                            question="Which behavior should take precedence?",
                        )
                    )
    return conflicts
