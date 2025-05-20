"""Generate simplified API reference from FastAPI app."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

# Work around module/package name clash
spec = importlib.util.spec_from_file_location(
    "legion.orchestrator", ROOT / "legion" / "orchestrator.py"
)
module = importlib.util.module_from_spec(spec)
sys.modules["legion.orchestrator"] = module
spec.loader.exec_module(module)

from interface.main import app


def main() -> None:
    schema = app.openapi()
    lines = ["# API Reference", ""]
    for path, methods in schema.get("paths", {}).items():
        for method, detail in methods.items():
            summary = detail.get("summary", "")
            lines.append(f"## {method.upper()} {path}")
            if summary:
                lines.append(summary)
            lines.append("")
    Path("docs/API_REFERENCE.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
