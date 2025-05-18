import sys
from tests.middleware.yaml_stub import yaml
from tests.middleware.orchestrator_stub import orchestrator_stub

# Inject YAML stub if pyyaml is missing
if 'yaml' not in sys.modules:
    sys.modules['yaml'] = yaml

# Avoid heavy orchestrator dependencies during import
sys.modules.setdefault('legion.orchestrator', orchestrator_stub)
