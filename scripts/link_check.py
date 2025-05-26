#!/usr/bin/env python3
import pathlib
import re
import sys
import urllib.parse

bad=[]
for md in pathlib.Path('docs').rglob('*.md'):
    text=md.read_text()
    for ln,line in enumerate(text.splitlines(),1):
        for tgt in re.findall(r'\[.+?\]\(([^)]+)\)', line):
            url = urllib.parse.urlparse(tgt)
            if url.scheme:
                continue
            path = url.path
            if not path:
                continue
            p=(md.parent / path).resolve()
            if not p.exists():
                bad.append(f"{md}:{ln}: {tgt}")
if bad:
    print("\n".join(bad))
    sys.exit(1)
print("[LINK-CHECK] PASS")
