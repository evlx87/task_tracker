from typing import List
from uuid import UUID

from pydantic import EmailStr, BaseModel


class BaseEmployeeSchema(BaseModel):
    """Базовая схема для представления информации о сотруднике без UUID."""
    email: EmailStr
    last_name: str
    first_name: str
    patronymic: str | None = None
    post: str | None = None

    class Config:
        """
        Настройки модели.

        Attributes:
        -----------
        from_attributes : bool      Позволяет создавать модель из словаря атрибутов.
        population_by_name : bool   Позволяет заполнять модель из словаря по именам атрибутов.
        arbitrary_types_allowed : bool  Разрешение использования произвольных типов данных.
        json_schema_extra : dict    Дополнительная информация для генерации JSON-схемы с примерами значений.
        """
        from_attributes = True
        population_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "email": "example@test.com",
                "last_name": "Иванов",
                "first_name": "Иван",
                "patronymic": "Иванович",
                "post": "Инженер"
            }
        }


class EmployeeSchema(BaseEmployeeSchema):
    """Схема для представления информации о сотруднике с UUID."""
    id: UUID


class EmployeeCreateUpdateSchema(BaseEmployeeSchema):
    """Схема для создания или обновления информации о сотруднике."""


class EmployeeList(BaseModel):
    """Схема для представления списка сотрудников."""
    employees: List[EmployeeSchema]
