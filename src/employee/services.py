from fastapi import APIRouter, Depends, status, HTTPException, Body
from fastapi.openapi.models import Response
from sqlalchemy.orm import Session, joinedload

from src.db_connect import get_db
from src.employee.model import Employee
from src.employee.schema import EmployeeList, EmployeeCreateUpdateSchema

api_employee = APIRouter(tags=['Сотрудники'], prefix='/employees')


def count_tasks(s: Employee) -> int:
    """
    Функция для подсчета количества задач у сотрудника.

    Attributes:
    -----------
    s : Employee Объект сотрудника.

    Returns:
    --------
    int Количество задач у сотрудника.
    """
    return len(s.tasks)


@api_employee.get('/', response_model=EmployeeList)
def get_employees(db: Session = Depends(get_db)) -> dict:
    """
    Получение списка всех сотрудников.

    Attributes:
    -----------
    db : Session Сессия базы данных.

    Returns:
    --------
    dict Словарь с информацией о сотрудниках.
    """
    employees = db.query(Employee).all()
    print(employees)
    return {'status': 'success',
            'results': len(employees),
            'employees': employees}


@api_employee.get('/get/{employeeId}')
def get_employee(employeeId: str, db: Session = Depends(get_db)):
    """
    Получение информации о конкретном сотруднике по ID.

    Attributes:
    -----------
    employeeId : str    Идентификатор сотрудника.
    db : Session    Сессия базы данных.

    Returns:
    --------
    dict    Словарь с информацией о сотруднике.
    """
    employee = db.query(Employee).filter(
        Employee.id == employeeId).first()  # Ищем сотрудника по ID
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Сотрудник с id: {employeeId} не найден")
    return {"status": "success", "employee": employee}


@api_employee.post('/create', status_code=status.HTTP_201_CREATED)
def create_employees(payload: EmployeeCreateUpdateSchema = Body(),
                     db: Session = Depends(get_db)):
    """
    Создание нового сотрудника на основе предоставленных данных.

    Attributes:
    -----------
    payload : EmployeeCreateUpdateSchema Данные для создания нового сотрудника.
    db : Session Сессия базы данных.

    Returns:
    --------
    dict Словарь с информацией о созданном сотруднике.
    """
    new_employee = Employee(**payload.dict())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return {'status': 'success', 'employee': new_employee}


@api_employee.patch('/update/{employeeId}')
def update_employee(employeeId: str,
                    payload: EmployeeCreateUpdateSchema = Depends(),
                    db: Session = Depends(get_db)):
    """
    Обновление информации о сотруднике по его ID.

    Attributes:
    -----------
    employeeId : str    Идентификатор сотрудника.
    payload : EmployeeCreateUpdateSchema    Данные для обновления информации о сотруднике.
    db : Session    Сессия базы данных.
    """
    employee_query = db.query(Employee).filter(Employee.id == employeeId)
    db_employee = employee_query.first()

    if not db_employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Сотрудник с id: {employeeId} не найден')
    update_data = payload.dict(exclude_unset=True)
    employee_query.filter(Employee.id == employeeId).update(
        update_data, synchronize_session=False)
    db.commit()
    db.refresh(db_employee)
    return {"status": "success", "employee": db_employee}


@api_employee.delete('/del/{employeeId}')
def delete_employee(employeeId: str, db: Session = Depends(get_db)):
    """
    Удаление сотрудника по его ID.

    Attributes:
    -----------
    employeeId: str    Идентификатор сотрудника.
    db: Session    Сессия базы данных.

    Returns:
    --------
    dict    Результат удаления сотрудника.
    """
    employee = db.query(Employee).filter(Employee.id == employeeId).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Сотрудник с id: {employeeId} не найден')

    if employee.tasks:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"У сотрудника с id: {employeeId} есть назначенные задачи. Удаление невозможно!")

    db.query(Employee).filter(Employee.id == employeeId).delete()
    db.commit()

    return {"status": "success", "message": "Сотрудник успешно удален."}


@api_employee.get('/busy', response_model=EmployeeList)
def get_employees_busy(db: Session = Depends(get_db)) -> dict:
    """
    Получение списка занятых сотрудников, с сортировкой по количеству задач.

    Attributes:
    -----------
    db : Session Сессия базы данных.

    Returns:
    --------
    dict Словарь со списком занятых сотрудников, отсортированных по количеству задач.
    """
    employees_query = (db.query(Employee).options(joinedload(Employee.tasks)).
                       filter(Employee.tasks is not None).all())
    employees = []
    for employee in employees_query:
        if len(employee.tasks) != 0:
            employees.append(employee)
    employees = sorted(employees, key=count_tasks, reverse=True)

    return {'status': 'success',
            'results': len(employees),
            'employees': employees}


@api_employee.get('/free')
def get_employees_free(db: Session = Depends(get_db)):
    """
    Получение списка свободных сотрудников.

    Attributes:
    -----------
    db : Session Сессия базы данных.

    Returns:
    --------
    dict Словарь со свободными сотрудниками.
    """

    employees_query = db.query(Employee).all()
    employees = []
    for employee in employees_query:
        if len(employee.tasks) == 0:
            employees.append(employee)

    if len(employees) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Сотрудников без заданий не найдено')

    return {"status": "success", "employees": employees}
