import uuid  # Импорт библиотеки uuid для генерации уникальных идентификаторов

# Импорт необходимых полей и типов данных для работы с БД
from sqlalchemy import (Column, Integer, String, Text, ForeignKey, TIMESTAMP)
# Импорт типа UUID для работы с PostgreSQL
from sqlalchemy.dialects.postgresql import UUID
# Импорт функционала для определения отношений между таблицами
from sqlalchemy.orm import relationship

from src.employee.model import Base  # Импорт базовой модели базы данных

# Определение класса Task, наследующего базовую модель Base


class Task(Base):
    __tablename__ = 'task'  # Название таблицы в базе данных

    # Определение колонок таблицы task
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)  # Уникальный идентификатор задачи
    # Название задачи (строка, обязательное поле, уникальное)
    name = Column(String, nullable=False, unique=True)
    # Содержание задачи (текст, обязательное поле)
    content = Column(Text, nullable=False)
    # Период исполнения задачи (временная метка)
    period_of_execution = Column(TIMESTAMP(timezone=True))
    parent_id = Column(UUID(as_uuid=True), ForeignKey(
        'task.id'), nullable=True)  # Идентификатор родительской задачи
    # Статус задачи (целое число, обязательное поле, значение по умолчанию = 0)
    status = Column(Integer, nullable=False, default=0)
    # Идентификатор сотрудника, ответственного за задачу
    employee_id = Column(
        UUID(
            as_uuid=True),
        ForeignKey('employee.id'),
        nullable=True)

    # Определение отношений между таблицами
    # Отношение "многие к одному" с таблицей Employee
    employees = relationship("Employee", back_populates='tasks', lazy='joined')
    # Отношение "один ко многим" (дочерние задачи)
    child_task = relationship(
        "Task",
        back_populates='parent_task',
        lazy='joined')
    parent_task = relationship("Task", remote_side='Task.id', back_populates='child_task',  # Отношение "один ко многим" (родительская задача)
                               foreign_keys=[parent_id], lazy='joined')

    # Метод для представления объекта Task в виде строки
    def __repr__(self):
        return (f"Task(name='{self.name}', "
                f"content='{self.content}', "
                f"period_of_execution='{self.period_of_execution}', "
                f"parent_id='{self.parent_id}',"
                f"employee_id='{self.employee_id}',"
                f"status='{self.status}')")
