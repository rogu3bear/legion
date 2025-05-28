import json
import pathlib
import sys
import types

# Ensure project root is on path so `interface.main` can be imported when this
# script is executed from the `scripts/` directory.
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Provide lightweight stubs for optional dependencies that may be missing in the
# execution environment. This keeps imports from failing when generating the
# OpenAPI schema.
sys.modules.setdefault('flask', types.ModuleType('flask'))
handshake_stub = types.ModuleType('interface.api.v1.endpoints.handshake')
handshake_stub.bp = None
sys.modules['interface.api.v1.endpoints.handshake'] = handshake_stub

# Provide a minimal `jinja2` stub so FastAPI can load when Jinja2 is not
# installed in the environment running this script. Only the pieces accessed
# during FastAPI startup are defined.
if 'jinja2' not in sys.modules:
    jinja2_stub = types.SimpleNamespace(
        FileSystemLoader=lambda directory: None
        Environment=lambda **env_options: types.SimpleNamespace(globals={})
        pass_context=lambda fn: fn
        contextfunction=lambda fn: fn
    )
    sys.modules['jinja2'] = jinja2_stub

# Adjust import depending on FastAPI application location
from interface.main import app

schema = app.openapi()
path = pathlib.Path("docs/api/openapi.json")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(schema, indent=2))
