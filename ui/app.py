from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def status() -> jsonify:
    return jsonify({"status": "Legion UI running"})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
