from uuid import UUID
from typing import List

from pydantic import EmailStr, BaseModel


class BaseEmployeeSchema(BaseModel):
    """
    Базовая схема Сотрудник.
    Без uuid
    """
    email: EmailStr  # Поле для электронной почты с валидацией по формату EmailStr
    last_name: str  # Фамилия сотрудника
    first_name: str  # Имя сотрудника
    patronymic: str | None = None  # Отчество сотрудника (необязательное поле)
    post: str | None = None  # Должность сотрудника (необязательное поле)

    class Config:
        # Настройки модели
        from_attributes = True  # Позволяет создавать модель из словаря атрибутов
        population_by_name = True  # Позволяет заполнять модель из словаря по именам атрибутов
        arbitrary_types_allowed = True  # Разрешает использование произвольных типов данных
        json_schema_extra = {
            "example": {
                "email": "example@test.com",
                "last_name": "Иванов",
                "first_name": "Иван",
                "patronymic": "Иванович",
                "post": "Инженер"
            }
        }  # Дополнительная информация для генерации JSON-схемы с примерами значений


class EmployeeSchema(BaseEmployeeSchema):
    """
    Схема Сотрудник.
    Добавлен UUID
    """
    id: UUID  # Уникальный идентификатор сотрудника


class EmployeeCreateUpdateSchema(BaseEmployeeSchema):
    """
    Схема Сотрудник для создания/обновления.
    """


class EmployeeList(BaseModel):
    """
    Список заданий
    """
    employees: List[EmployeeSchema]  # Список объектов схемы EmployeeSchema, представляющих сотрудников
