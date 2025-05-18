from middleware.src.middleware.directive_compliance import DirectiveCompliance


def test_length_violation():
    dc = DirectiveCompliance()
    long_text = "x" * 2000
    status, details = dc.check(long_text, {"task_id": "1"})
    assert status == "non_compliant"
    assert "max_length_exceeded" in details.get("breach_type", "")


def test_prohibited_keyword_triggers_therapist():
    dc = DirectiveCompliance()
    text = "please sudo rm -rf /"
    status, details = dc.check(text, {"task_id": "1"})
    assert status == "therapist_triggered"
    assert "therapist_reason" in details


def test_missing_required_field():
    dc = DirectiveCompliance()
    status, details = dc.check("ok", {})
    assert status == "non_compliant"
    assert "missing_metadata" in details.get("breach_type", "")


def test_compliant_request():
    dc = DirectiveCompliance()
    status, details = dc.check("summarize", {"task_id": "1"}, agent_id="researcher_agent")
    assert status == "compliant"
    assert details["checks_failed"] == []
