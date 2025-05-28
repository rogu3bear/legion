#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from core.therapist import therapist_guard

class Dummy:
    disabled = False

    @therapist_guard("directive")
    def allowed(self):
        return "allowed"

    @therapist_guard("other")
    def blocked(self):
        return "blocked"

d = Dummy()
print(d.allowed())
print(d.blocked())

therapist_guard.enable(False)
print(d.blocked())
PY
