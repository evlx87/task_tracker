from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.openapi.models import Response
from sqlalchemy.orm import Session

from src.db_connect import get_db
from src.employee.model import Employee
from src.employee.services import count_tasks
from src.tasks.model import Task
from src.tasks.schema import TasksList, TaskCreateUpdateSchema

# Создание нового роутера APIRouter с тегом 'Tasks' и префиксом '/tasks'
api_task = APIRouter(tags=['Tasks'], prefix='/tasks')


@api_task.get('/', response_model=TasksList)
def get_tasks(db: Session = Depends(get_db),
              limit: int = 10, page: int = 1) -> dict:
    """
    Функция для получения списка задач с возможностью пагинации
    :param db: сессия базы данных
    :param limit: количество задач на страницу
    :param page: номер страницы
    :return: словарь с результатами запроса
    """
    skip = (page - 1) * limit
    tasks = db.query(Task).limit(limit).offset(skip).all()
    return {'status': 'success', 'results': len(tasks), 'tasks': tasks}


@api_task.get('/get/{taskId}')
def get_task(taskId: str, db: Session = Depends(get_db)):
    """
    Функция для получения задачи по её ID
    :param taskId: ID задачи
    :param db: сессия базы данных
    :return: словарь с информацией о задаче
    """
    task = db.query(Task).filter(Task.id == taskId).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Задание с id: {taskId} не найдено')
    return {"status": "success", "task": task}


# Создание новой задачи
@api_task.post('/create/', status_code=status.HTTP_201_CREATED)
def create_tasks(payload: TaskCreateUpdateSchema = Depends(),
                 db: Session = Depends(get_db)):
    """
    Функция для создания новой задачи на основе переданных данных
    :param payload: данные для создания задачи
    :param db: сессия базы данных
    :return: словарь с информацией о созданной задаче
    """
    new_task = Task(**payload.dict())
    if new_task.employee_id is not None and new_task.status == 0:
        new_task.status = 1
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {'status': 'success',
            'task': new_task}


# Обновление задачи по ID
@api_task.patch('/update/{taskId}')
def update_task(taskId: str, payload: TaskCreateUpdateSchema = Depends(),
                db: Session = Depends(get_db)):
    """
    Функция для обновления задачи по её ID
    :param taskId: ID задачи для обновления
    :param payload: данные для обновления задачи
    :param db: сессия базы данных
    :return: словарь с информацией об обновленной задаче
    """
    task_query = db.query(Task).filter(Task.id == taskId)
    task = task_query.first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Задание с id: {taskId} не найдено')
    update_data = payload.dict(exclude_unset=True)
    task_query.filter(Task.id == taskId).update(
        update_data, synchronize_session=False)
    db.commit()
    db.refresh(task)
    return {"status": "success", "task": task}


# Удаление задачи по ID
@api_task.delete('/del/{taskId}')
def delete_task(taskId: str, db: Session = Depends(get_db)):
    """
    Функция для удаления задачи по её ID
    :param taskId: ID задачи для удаления
    :param db: сессия базы данных
    :return: статус 204 при успешном удалении
    """
    task_query = db.query(Task).filter(Task.id == taskId)
    task = task_query.first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Задание с id: {taskId} не найдено')
    task_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Получение списка важных задач
@api_task.get('/important')
def get_important_tasks(db: Session = Depends(get_db),
                        limit: int = 10, page: int = 1):
    """
    Функция для получения списка важных задач с учетом родительских задач
    :param db: сессия базы данных
    :param limit: количество задач на страницу
    :param page: номер страницы
    :return: словарь с результатами запроса
    """
    skip = (page - 1) * limit
    tasks = (db.query(Task).filter(Task.status == 0).
             limit(limit).offset(skip).all())
    tasks_ret = []
    for task in tasks:
        if task.parent_id is not None and task.parent_task.status == 1:
            tasks_ret.append(task)

    return {'status': 'success', 'results': len(tasks_ret), 'tasks': tasks_ret}


# Получение списка незадействованных задач
@api_task.get('/free')
def get_free_tasks(db: Session = Depends(get_db),
                   limit: int = 10, page: int = 1):
    """
    Функция для получения списка незадействованных задач (статус задачи = 0)
    :param db: сессия базы данных
    :param limit: количество задач на страницу
    :param page: номер страницы
    :return: словарь с результатами запроса
    """
    skip = (page - 1) * limit
    tasks = (db.query(Task).filter(Task.status == 0).
             limit(limit).offset(skip).all())

    return {'status': 'success', 'results': len(tasks), 'tasks': tasks}


# Назначение исполнителя для важной задачи
@api_task.patch('/set_employee/{taskId}')
def set_employee_important_task(taskId: str, db: Session = Depends(get_db)):
    """
    Функция для установки исполнителя для важной задачи
    :param taskId: ID задачи
    :param db: сессия базы данных
    :return: словарь с информацией об обновленной задаче
    """
    task_query = db.query(Task).filter(Task.id == taskId)
    task = task_query.first()
    employee_parent = task.parent_task
    payload = TaskCreateUpdateSchema(
        name=task.name,
        content=task.content,
        period_of_execution=task.period_of_execution,
        parent_id=task.parent_id,
        status=task.status,
        employee_id=task.employee_id
    )

    # Получаем сотрудников, ищем свободного сотрудника, без задач
    employees_query = db.query(Employee).all()
    employees_query = sorted(employees_query, key=count_tasks)
    employee_min = employees_query[0]
    employees_free = []
    for employee in employees_query:
        if employee.count_task() == 0:
            employees_free.append(employee)
    employee_free = employee_min
    # Если свободный есть, берем первый и обновляем задание.
    if len(employees_free) > 0:
        employee_free = employees_free[0]
    else:
        # Если нет свободного, ищем с наименьшим количеством задач и сотрудника,
        # имеющего в работе родительскую задачу.
        if employee_parent.count_task() < employee_min.count_task() + 3:
            employee_free = employee_parent

    payload.employee_id = employee_free.id
    payload.status = 1
    update_data = payload.dict(exclude_unset=True)
    # Если нет, ищем дальше.
    task_query.filter(Task.id == taskId).update(
        update_data, synchronize_session=False)
    db.commit()
    db.refresh(task)
    return {"status": "success", "task": task}
