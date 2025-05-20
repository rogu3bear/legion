import sys
import types

def apply_stubs():
    names = [
        "openai",
        "discord",
        "discord.ext",
        "discord.ext.commands",
        "pytest",
        "httpx",
        "dotenv",
    ]
    for name in names:
        if name not in sys.modules:
            module = types.ModuleType(name)
            sys.modules[name] = module
        # ensure submodules for discord.ext
        if name == "discord.ext" and "discord.ext.commands" not in sys.modules:
            sys.modules["discord.ext.commands"] = types.ModuleType("discord.ext.commands")


