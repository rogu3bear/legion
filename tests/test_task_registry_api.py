from fastapi.testclient import TestClient

from interface.main import app

client = TestClient(app)


def test_create_and_get_task():
    payload = {"id": "task1", "tags": ["demo"], "owner": "tester"}
    response = client.post("/api/v1/registry/tasks/", json=payload)
    assert response.status_code == 201
    task = response.json()
    assert task["id"] == "task1"

    get_resp = client.get(f"/api/v1/registry/tasks/{task['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["owner"] == "tester"


def test_filter_tasks():
    client.post("/api/v1/registry/tasks/", json={"id": "task2", "tags": ["t"], "owner": "bob"})
    resp = client.get("/api/v1/registry/tasks", params={"owner": "bob"})
    assert resp.status_code == 200
    body = resp.json()
    assert any(t["id"] == "task2" for t in body)


def test_delete_task():
    client.post("/api/v1/registry/tasks/", json={"id": "task3", "tags": [], "owner": "c"})
    del_resp = client.delete("/api/v1/registry/tasks/task3")
    assert del_resp.status_code == 204
    get_resp = client.get("/api/v1/registry/tasks/task3")
    assert get_resp.status_code == 404
