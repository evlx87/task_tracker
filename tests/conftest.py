import uuid
import pytest
from fastapi.testclient import TestClient

from main import app
from src.db_connect import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.employee.model import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
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
def create_test_task():
    unique_name = f"Test Task {uuid.uuid4()}"
    test_task_payload = {
        "name": unique_name,
        "content": "This is a test task",
        "period_of_execution": "2023-12-31",
        "status": 0,
        "employee_id": None,
        "parent_id": None
    }
    response = client.post("/tasks/create/", json=test_task_payload)
    assert response.status_code == 201
    return response.json()["task"]["id"]


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
    assert response.status_code == 201
    return response.json()["employee"]["id"]
