def safe_load(file):
    """Stub for yaml.safe_load"""
    return {"directives": {"run": {"description": "Run directive"}, "stop": {"description": "Stop directive"}}}

class YAMLError(Exception):
    """Stub for yaml.YAMLError"""
    pass
