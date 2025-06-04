import ast
from pathlib import Path
from typing import List, Tuple

AGENT_ROOT = Path("legion/agents")
ORCHESTRATOR_FILES = [
    Path("legion/orchestrator/__init__.py"),
    Path("legion/pipeline/Orchestrator.py"),
]
OUTPUT_ROOT = Path('docs/agents')


def extract_methods(cls: ast.ClassDef) -> List[Tuple[str, List[str], str]]:
    methods = []
    for node in cls.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith('_'):
            args = [a.arg for a in node.args.args if a.arg != 'self']
            doc = ast.get_docstring(node)
            summary = doc.splitlines()[0] if doc else 'No summary'
            methods.append((node.name, args, summary))
    return methods


def parse_file(path: Path) -> List[Tuple[str, str, List[Tuple[str, List[str], str]]]]:
    try:
        tree = ast.parse(path.read_text())
    except Exception:
        return []
    classes = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and (
            node.name.endswith("Agent") or node.name == "Orchestrator"
        ):
            doc = ast.get_docstring(node)
            role = doc.splitlines()[0] if doc else 'No description'
            methods = extract_methods(node)
            classes.append((node.name, role, methods))
    return classes


def generate_docs() -> None:
    files = [
        p
        for p in AGENT_ROOT.rglob("*.py")
        if p.name not in {"__init__.py", "base.py"}
    ]
    files.extend(f for f in ORCHESTRATOR_FILES if f.exists())
    for py_file in files:
        for name, role, methods in parse_file(py_file):
            out_path = OUTPUT_ROOT / f"{name.lower()}.md"
            lines = [f"# {name}", '', f"**Role:** {role}", '', '## Methods', '']
            for m, args, summary in methods:
                arg_str = ', '.join(args)
                lines.append(f"- `{m}({arg_str})` - {summary}")
            if not out_path.parent.exists():
                out_path.parent.mkdir(parents=True)
            content = "\n".join(lines)
            if not content.endswith("\n"):
                content += "\n"
            out_path.write_text(content)


if __name__ == '__main__':
    generate_docs()
