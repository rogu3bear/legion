import sys
import types
import pathlib

# Add stubs directory to sys.path
stubs = pathlib.Path(__file__).parent / "stubs"
if str(stubs) not in sys.path:
    sys.path.insert(0, str(stubs))

# Create stub modules for direct imports
for name in ("openai", "discord", "discord.ext", "pytest"):
    sys.modules[name] = types.ModuleType(name)
