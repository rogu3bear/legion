# Therapist Validation Placeholder

This update introduces a very small validation helper for therapist task payloads along with a unit test.

```python
# legion/agents/therapist/validation.py
from typing import Any, Dict, Optional

# ... existing functions ...

def validate_task(task: dict) -> bool:
    """Validates a Legion task dictionary for required fields and types."""
    # TODO: Replace with schema-based validation
    required_keys = ["id", "agent", "payload"]
    return all(key in task for key in required_keys)
```

```python
# tests/agents/test_therapist.py
def test_validate_task_basic():
    valid_task = {"id": "123", "agent": "echo", "payload": {}}
    assert validate_task(valid_task)

    invalid_task = {"id": "456", "payload": {}}
    assert not validate_task(invalid_task)
```
