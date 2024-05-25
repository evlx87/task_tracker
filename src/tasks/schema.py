from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class BaseTaskSchema(BaseModel):
    """
    Базовая схема Задание.
    Без UUID

    Attributes:
    -----------
        name : str  Название задания.
        content : str   Описание задания.
        period_of_execution : Optional[datetime]    Период выполнения задания.
        parent_id : Optional[UUID]  ID родительского задания.
        status : int    Статус задания.
        employee_id : Optional[UUID]    ID сотрудника.
    """
    name: str  # Название задания
    content: str  # Описание задания
    period_of_execution: datetime | None = None  # Период выполнения задания
    parent_id: UUID | None = None  # ID родительского задания
    status: int = 0  # Статус задания
    employee_id: UUID | None = None  # ID сотрудника

    class Config:
        """
        Настройки схемы
        """
        from_attributes = True  # Генерировать настройки из атрибутов
        # Разрешить передачу значений аргументов через именованные аргументы
        population_by_name = True
        arbitrary_types_allowed = True  # Разрешить произвольные типы данных
        json_schema_extra = {
            "example": {
                "name": "Задание1",
                "content": "Описание задания",
                "period_of_execution": "2024-04-28 19:35:00+03:00",
                "status": "0"
            }
        }


class TaskSchema(BaseTaskSchema):
    """
    Схема Задание.
    Добавлен UUID

    Attributes:
    -----------
        id : UUID   ID задания.
    """
    id: UUID  # ID задания


class TaskCreateUpdateSchema(BaseTaskSchema):
    """
    Схема Задание для создания/обновления.
    """


class TasksList(BaseModel):
    """
    Список заданий

    Attributes:
    -----------
        tasks : List[TaskSchema]    Список заданий.
    """
    tasks: List[TaskSchema]
