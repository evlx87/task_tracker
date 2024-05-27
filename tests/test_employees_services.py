import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from src.db_connect import get_db
from src.employee.model import Base
from src.employee.schema import EmployeeCreateUpdateSchema

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def create_test_employee():
    unique_name = f"TestEmployee{uuid.uuid4()}"
    test_employee_payload = {
        "first_name": "Test",
        "last_name": "Employee",
        "name": unique_name,
        "email": f"{unique_name}@example.com"
    }

    response = client.post("/employees/create", json=test_employee_payload)
    if response.status_code != 201:
        print(response.json())
    assert response.status_code == 201, f"Failed to create test employee: {response.json()}"
    return response.json()["employee"]["id"]


def test_create_employee():
    unique_name = f"TestEmployee{uuid.uuid4()}"
    test_employee_payload = {
        "first_name": "Test",
        "last_name": "Employee",
        "name": unique_name,
        "email": f"{unique_name}@example.com"
    }
    assert EmployeeCreateUpdateSchema(**test_employee_payload)
    response = client.post("/employees/create", json=test_employee_payload)
    assert response.status_code == 201, f"Response JSON: {response.json()}"
    assert response.json()["status"] == "success"


def test_get_employees_free():
    response = client.get("/employees/free/")
    assert response.status_code == 200 or response.status_code == 404
    if response.status_code == 200:
        response_json = response.json()
        assert "status" in response_json, f"Response JSON: {response_json}"
        assert response_json["status"] == "success"
    else:
        response_json = response.json()
        assert "detail" in response_json, f"Response JSON: {response_json}"
        assert response_json["detail"] == 'Сотрудников без заданий не найдено'
