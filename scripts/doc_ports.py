#!/usr/bin/env python3
"""
Auto-generate current port map into docs/monitoring.md
"""

import re
from pathlib import Path
from typing import Dict

ENV_FILE = Path(".env.ports")
DOC_FILE = Path("docs/monitoring.md")
PORT_MAP_HEADER = "### Current Port Map"


def parse_env() -> Dict[str, str]:
    ports = {}
    if not ENV_FILE.exists():
        return ports
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        svc = key.replace("PORT_ALLOCATOR_", "").lower()
        ports[svc] = val
    return ports


def generate_table(ports: Dict[str, str]) -> str:
    lines = [
        f"{PORT_MAP_HEADER}\n",
        "| Service        | Host Port |\n",
        "| -------------- | --------- |\n",
    ]
    for svc, port in sorted(ports.items()):
        lines.append(f"| {svc:<14} | {port:<9} |\n")
    return "".join(lines)


def update_doc(table_md: str) -> None:
    text = DOC_FILE.read_text()
    # Replace existing port map section
    pattern = rf"{PORT_MAP_HEADER}[\s\S]*?(?=^## |\Z)"
    new_text, count = re.subn(pattern, table_md, text, flags=re.MULTILINE)
    if count == 0:
        # Append at end if no existing header found
        new_text = text + "\n" + table_md
    DOC_FILE.write_text(new_text)


def main() -> None:
    ports = parse_env()
    table_md = generate_table(ports)
    update_doc(table_md)


if __name__ == "__main__":
    main()
