import json
import types

yaml = types.ModuleType("yaml")


def safe_load(stream):
    if hasattr(stream, "read"):
        data = stream.read()
    else:
        data = stream
    if not data:
        return {}
    return json.loads(data)


def dump(data, stream=None):
    text = json.dumps(data)
    if stream:
        if hasattr(stream, "write"):
            stream.write(text)
        else:
            with open(stream, "w") as fh:
                fh.write(text)
    return text


yaml.safe_load = safe_load
yaml.dump = dump
yaml.YAMLError = Exception
