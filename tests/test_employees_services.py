from tests.conftest import client, create_test_employee


def test_create_employee(create_test_employee):
    test_employee_id = create_test_employee
    test_employee_payload = {
        "first_name": "Test",
        "last_name": "Employee",
        "name": f"TestEmployee{test_employee_id}",
        "email": f"testemployee{test_employee_id}@example.com"
    }
    response = client.post("/employees/create/", json=test_employee_payload)
    assert response.status_code == 201
    assert response.json()["status"] == "success"


def test_get_employees_free():
    response = client.get("/employees/free/")
    assert response.status_code == 200 or response.status_code == 404
    if response.status_code == 200:
        response_json = response.json()
        assert "status" in response_json
        assert response_json["status"] == "success"
    else:
        response_json = response.json()
        assert "detail" in response_json
        assert response_json["detail"] == 'Сотрудников без заданий не найдено'
