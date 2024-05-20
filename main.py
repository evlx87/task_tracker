import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session, joinedload

# Импорт функций и объектов из других модулей
from src.db_connect import create_db, engine, get_db, DB_HOST
# Импорт сущностей модели сотрудника
from src.employee.model import Base, Employee
# Импорт функций и роутера для работы сотрудниками
from src.employee.services import api_employee, count_tasks
# Импорт функций и роутера для работы с задачами
from src.tasks.services import api_task

create_db()  # Создание базы данных

Base.metadata.create_all(bind=engine)  # Создание таблиц на основе модели

app = FastAPI(
    # Создание экземпляра FastAPI с указанием названия
    title="Трекер задач сотрудников",
)

# Подключение роутера для работы с сотрудниками
app.include_router(api_employee)
app.include_router(api_task)  # Подключение роутера для работы с задачами


@app.get('/')
def root(db: Session = Depends(get_db)):
    employees = db.query(Employee).options(joinedload(
        Employee.tasks)).all()  # Запрос сотрудников с их задачами
    # Сортировка сотрудников по количеству задач
    employees = sorted(employees, key=count_tasks, reverse=True)
    return {'status': 'success',
            'results': len(employees),
            'employees': employees}  # Возврат JSON с информацией о сотрудниках


# Запуск сервера локально
if __name__ == '__main__':
    # Запуск приложения с указанным хостом и портом
    uvicorn.run(app, host=DB_HOST, port=8000)
