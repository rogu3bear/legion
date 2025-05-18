"""Validate that configured ports fall within 7801-7810.

The script also scans Python, YAML, JS and TS files for hard-coded ports.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
import re

RANGE_START = 7801
RANGE_END = 7810

ENV_FILE = Path(".env.ports")


def load_ports() -> dict[str, int]:
    ports: dict[str, int] = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.startswith("PORT_ALLOCATOR_"):
                try:
                    ports[k] = int(v)
                except ValueError:
                    print(f"Invalid port value for {k}: {v}")
    return ports


def main() -> int:
    ports = load_ports()
    invalid = []
    for key, port in ports.items():
        if not (RANGE_START <= port <= RANGE_END):
            invalid.append((key, port))
    if invalid:
        for k, p in invalid:
            print(f"Port {k}={p} out of allowed range {RANGE_START}-{RANGE_END}")
        return 1
    files = list(Path(".").rglob("*"))
    pattern = re.compile(r"\b(\d{4,5})\b")
    for file in files:
        if file.suffix.lower() in {".py", ".yaml", ".yml", ".js", ".ts"}:
            try:
                text = file.read_text(encoding="utf-8")
            except Exception:
                continue
            for match in pattern.findall(text):
                port = int(match)
                if RANGE_START <= port <= RANGE_END:
                    continue
                if 1024 <= port <= 65535:
                    invalid.append((str(file), port))

    if invalid:
        for src, port in invalid:
            print(f"Port {port} in {src} out of range {RANGE_START}-{RANGE_END}")
        return 1
    print("All ports valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
