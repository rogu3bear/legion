import sys
import types

for name in ("openai", "discord", "discord.ext", "pytest"):
    sys.modules[name] = types.ModuleType(name)
