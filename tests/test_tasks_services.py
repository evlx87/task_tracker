from tests.conftest import client, create_test_task


def test_create_task(create_test_task):
    test_task_id = create_test_task
    test_task_payload = {
        "name": f"Test Task {test_task_id}",
        "content": "This is a test task",
        "period_of_execution": "2023-12-31",
        "status": 0,
        "employee_id": None,
        "parent_id": None
    }
    response = client.post("/tasks/create/", json=test_task_payload)
    assert response.status_code == 201
    assert response.json()["status"] == "success"


def test_get_important_tasks():
    response = client.get("/tasks/important/")
    assert response.status_code == 200
    response_json = response.json()
    assert "status" in response_json
    assert response_json["status"] == "success"


def test_get_free_tasks():
    response = client.get("/tasks/free/")
    assert response.status_code == 200
    response_json = response.json()
    assert "status" in response_json
    assert response_json["status"] == "success"
