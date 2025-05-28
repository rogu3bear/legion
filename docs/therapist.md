<!-- File: docs/therapist.md -->

# Therapist Guard

`therapist_guard` is a lightweight decorator used to gate agent calls. It performs a few sanity checks before allowing the underlying function to execute. When a check fails the call returns a small JSON payload and a warning is logged.

## Usage

```python
from core.therapist import therapist_guard

class EchoAgent(BaseAgent):
    @therapist_guard("directive")
    async def handle_echo(self, message: str) -> str:
        ...
```

### Disabling

For local development the guard can be disabled globally:

```python
from core.therapist import therapist_guard
therapist_guard.enable(False)
```


