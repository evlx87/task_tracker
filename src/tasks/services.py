from fastapi import APIRouter, Depends, status, HTTPException, Body
from fastapi.openapi.models import Response
from sqlalchemy.orm import Session

from src.db_connect import get_db
from src.employee.model import Employee
from src.employee.services import count_tasks
from src.tasks.model import Task
from src.tasks.schema import TasksList, TaskCreateUpdateSchema

api_task = APIRouter(tags=['Tasks'], prefix='/tasks')


@api_task.get('/', response_model=TasksList)
def get_tasks(db: Session = Depends(get_db),
              limit: int = 10, page: int = 1) -> dict:
    """
    Функция для получения списка задач с возможностью пагинации

    Attributes:
    -----------
        db: Session Cессия базы данных
        limit: int Количество задач на страницу
        page: int Номер страницы

    :return: dict Словарь с результатами запроса
    """
    skip = (page - 1) * limit
    tasks = db.query(Task).limit(limit).offset(skip).all()
    return {'status': 'success', 'results': len(tasks), 'tasks': tasks}


@api_task.get('/get/{taskId}')
def get_task(taskId: str, db: Session = Depends(get_db)):
    """
    Функция для получения задачи по её ID

    Attributes:
    -----------
        taskId: str ID задачи
        db: Session сессия базы данных

    :return: dict   словарь с информацией о задаче
    """
    task = db.query(Task).filter(Task.id == taskId).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Задание с id: {taskId} не найдено')
    return {"status": "success", "task": task}


@api_task.post('/create/', status_code=status.HTTP_201_CREATED)
def create_tasks(payload: TaskCreateUpdateSchema = Body(),
                 db: Session = Depends(get_db)):
    """
    Функция для создания новой задачи на основе переданных данных

    Attributes:
    -----------
        payload: TaskCreateUpdateSchema данные для создания задачи
        db: Session сессия базы данных

    :return: dict словарь с информацией о созданной задаче
    """
    new_task = Task(**payload.dict())
    if new_task.employee_id is not None and new_task.status == 0:
        new_task.status = 1
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {'status': 'success',
            'task': new_task}


@api_task.patch('/update/{taskId}')
def update_task(taskId: str, payload: TaskCreateUpdateSchema = Depends(),
                db: Session = Depends(get_db)):
    """
    Функция для обновления задачи по её ID

    Attributes:
    -----------
        taskId: str     ID задачи для обновления
        payload: TaskCreateUpdateSchema     данные для обновления задачи
        db: Session     сессия базы данных

    :return: dict   словарь с информацией об обновленной задаче
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


@api_task.delete('/del/{taskId}')
def delete_task(taskId: str, db: Session = Depends(get_db)):
    """
    Функция для удаления задачи по её ID

    Attributes:
    -----------
        taskId: str     ID задачи для удаления
        db: Session     сессия базы данных

    :return: Response   статус 204 при успешном удалении
    """
    task_query = db.query(Task).filter(Task.id == taskId)
    task = task_query.first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Задание с id: {taskId} не найдено')
    task_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@api_task.get('/important')
def get_important_tasks(db: Session = Depends(get_db),
                        limit: int = 10, page: int = 1):
    """
    Функция для получения списка важных задач с учетом родительских задач

    Attributes:
    -----------
        db: Session сессия базы данных
        limit: int количество задач на страницу
        page: int номер страницы

    :return: dict словарь с результатами запроса
    """
    skip = (page - 1) * limit
    tasks = (db.query(Task).filter(Task.status == 0).
             limit(limit).offset(skip).all())
    tasks_ret = []
    for task in tasks:
        if task.parent_id is not None and task.parent_task.status == 1:
            tasks_ret.append(task)

    return {'status': 'success', 'results': len(tasks_ret), 'tasks': tasks_ret}


@api_task.get('/free')
def get_free_tasks(db: Session = Depends(get_db),
                   limit: int = 10, page: int = 1):
    """
    Функция для получения списка незадействованных задач (статус задачи = 0)

    Attributes:
    -----------
        db: Session сессия базы данных
        limit: int  количество задач на страницу
        page: int   номер страницы

    :return: dict
        словарь с результатами запроса
    """
    skip = (page - 1) * limit
    tasks = (db.query(Task).filter(Task.status == 0).
             limit(limit).offset(skip).all())

    return {'status': 'success', 'results': len(tasks), 'tasks': tasks}


@api_task.patch('/set_employee/{taskId}')
def set_employee_important_task(taskId: str, db: Session = Depends(get_db)):
    """
    Функция для установки исполнителя для важной задачи

    Attributes:
    -----------
        taskId: str  ID задачи
        db: Session сессия базы данных

    :return: dict   словарь с информацией об обновленной задаче
    """
    task_query = db.query(Task).filter(Task.id == taskId)
    task = task_query.first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Задание с id: {taskId} не найдено')

    employee_parent = task.parent_task

    parent_task_count = employee_parent.count_task() if employee_parent else 0

    payload = TaskCreateUpdateSchema(
        name=task.name,
        content=task.content,
        period_of_execution=task.period_of_execution,
        parent_id=task.parent_id,
        status=task.status,
        employee_id=task.employee_id
    )

    employees_query = db.query(Employee).all()
    employees_query = sorted(employees_query, key=count_tasks)
    employee_min = employees_query[0]

    employees_free = [
        employee for employee in employees_query if employee.count_task() == 0]
    employee_free = employee_min

    if employees_free:
        employee_free = employees_free[0]
    else:
        if employee_parent and parent_task_count < employee_min.count_task() + 3:
            employee_free = employee_parent

    payload.employee_id = employee_free.id
    payload.status = 1
    update_data = payload.dict(exclude_unset=True)

    task_query.update(update_data, synchronize_session=False)
    db.commit()
    db.refresh(task)

    return {"status": "success", "task": task}
