from legion.agents.therapist.validation import validate_task


def test_validate_task_basic():
    valid_task = {"id": "123", "agent": "echo", "payload": {}}
    assert validate_task(valid_task)

    invalid_task = {"id": "456", "payload": {}}
    assert not validate_task(invalid_task)
