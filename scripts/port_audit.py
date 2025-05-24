"""Scan the repository for unexpected port numbers."""

import os
import re
import sys

ALLOWED = {str(p) for p in range(7801, 7811)}
PORT_PATTERN = re.compile(r"(?<!\d)(\d{4})(?!\d)")


def main() -> None:
    mismatches: list[str] = []
    for root, _dirs, files in os.walk("."):
        if ".git" in root.split(os.sep):
            continue
        for fname in files:
            path = os.path.join(root, fname)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for lineno, line in enumerate(f, 1):
                        for match in PORT_PATTERN.finditer(line):
                            port = match.group(1)
                            if port not in ALLOWED:
                                mismatches.append(f"{path}:{lineno}:{port}")
            except Exception:
                continue
    if mismatches:
        print("Found port mismatches:")
        for m in mismatches:
            print(m)
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
