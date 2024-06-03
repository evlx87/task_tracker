import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session, joinedload

from src.db_connect import create_db, engine, get_db, DB_HOST
from src.employee.model import Base, Employee
from src.employee.services import api_employee, count_tasks
from src.tasks.services import api_task

create_db()

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Трекер задач сотрудников",)
app.include_router(api_employee)
app.include_router(api_task)


@app.get('/')
def root(db: Session = Depends(get_db)):
    employees = db.query(Employee).options(joinedload(Employee.tasks)).all()
    employees = sorted(employees, key=count_tasks, reverse=True)
    return {'status': 'success',
            'results': len(employees),
            'employees': employees}


if __name__ == '__main__':
    uvicorn.run(app, host=DB_HOST, port=8000)
