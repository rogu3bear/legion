from flask import Flask, jsonify
from flask_cors import CORS
import os
import yaml

app = Flask(__name__)
CORS(app)


@app.route("/")
def status() -> jsonify:
    return jsonify({"status": "Legion UI running"})

@app.route("/agents")
def list_agents():
    configs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../legion/configs"))
    files = [f[:-5] for f in os.listdir(configs_dir) if f.endswith(".yaml")]
    return jsonify({"agents": files})

@app.route("/agents/<agent_name>")
def get_agent(agent_name):
    configs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../legion/configs"))
    path = os.path.join(configs_dir, f"{agent_name}.yaml")
    if not os.path.exists(path):
        return jsonify({"error": "Agent not found"}), 404
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return jsonify({agent_name: cfg})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
