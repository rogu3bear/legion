import sys, pathlib, difflib, subprocess
spec = pathlib.Path(sys.argv[1]).read_text().splitlines()
changed = subprocess.getoutput("git diff --name-only $(git merge-base origin/main HEAD)").splitlines()
missing = [line for line in spec if line.strip().startswith("*") and line.split("*")[-1].strip() not in changed]
print("\n".join(missing)) 