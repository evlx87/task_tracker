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

# Создание базы данных
create_db()

# Создание таблиц на основе модели
Base.metadata.create_all(bind=engine)

# Создание экземпляра FastAPI с указанием названия
app = FastAPI(title="Трекер задач сотрудников",)

# Подключение роутера для работы с сотрудниками
app.include_router(api_employee)
# Подключение роутера для работы с задачами
app.include_router(api_task)


@app.get('/')
def root(db: Session = Depends(get_db)):
    # Запрос сотрудников с их задачами
    employees = db.query(Employee).options(joinedload(Employee.tasks)).all()
    # Сортировка сотрудников по количеству задач
    employees = sorted(employees, key=count_tasks, reverse=True)
    # Возврат JSON с информацией о сотрудниках
    return {'status': 'success',
            'results': len(employees),
            'employees': employees}


# Запуск сервера локально
if __name__ == '__main__':
    # Запуск приложения с указанным хостом и портом
    uvicorn.run(app, host=DB_HOST, port=8000)
