from app.services.security import assess_security


def test_document_requirement_generates_data_protection_risk() -> None:
    items = assess_security("Applicants upload bank statements.", ["functional"])
    assert items[0].category == "data_protection"
    assert items[0].likelihood * items[0].impact == 15


def test_access_requirement_generates_access_control_finding() -> None:
    items = assess_security("Underwriters access applicant records.", ["security"])
    assert any(item.category == "access_control" for item in items)


def test_unrelated_requirement_does_not_invent_finding() -> None:
    assert assess_security("The product supports fixed interest rates.", ["functional"]) == []
