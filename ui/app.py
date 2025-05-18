from flask import Flask, jsonify
from flask_cors import CORS
from pathlib import Path
import yaml
from legion.ports import get_port

app = Flask(__name__)
CORS(app)


@app.route("/")
def status() -> jsonify:
    return jsonify({"status": "Legion UI running"})

@app.route("/agents")
def list_agents() -> jsonify:
    """Return the list of available agent configuration names."""
    configs_dir = Path(__file__).resolve().parent.parent / "legion" / "configs"
    files = [p.stem for p in configs_dir.iterdir() if p.suffix == ".yaml"]
    return jsonify({"agents": files})

@app.route("/agents/<agent_name>")
def get_agent(agent_name: str) -> jsonify:
    """Return the YAML config for a specific agent."""
    configs_dir = Path(__file__).resolve().parent.parent / "legion" / "configs"
    path = configs_dir / f"{agent_name}.yaml"
    if not path.exists():
        return jsonify({"error": "Agent not found"}), 404
    with path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return jsonify({agent_name: cfg})


if __name__ == "__main__":
    app.run(debug=True, port=get_port("PORT_ALLOCATOR_UI_BACKEND"))
