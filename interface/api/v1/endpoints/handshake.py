from flask import Blueprint, jsonify, request, abort
from legion.registration import service
from legion.task_queue import queue

bp = Blueprint("handshake", __name__)

@bp.post("/agent/register")
def register_agent():
    payload = request.get_json(force=True)
    result = service.handle(payload)
    if "error" in result:
        if result["error"] == "unauthorized":
            return jsonify(result), 401
        return jsonify(result), 400
    return jsonify(result)

@bp.get("/queue/summary")
def queue_summary():
    return jsonify(queue.summary())

@bp.get("/queue/task/<task_id>")
def queue_task_detail(task_id):
    task = queue.get(task_id)
    if not task:
        abort(404)
    return jsonify(task.__dict__)
