import uuid

from sqlalchemy import (Column, Integer, String, Text, ForeignKey, TIMESTAMP)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.employee.model import Base


class Task(Base):
    """
    Модель задачи.

    Attributes:
    -----------
       id : uuid.UUID   Уникальный идентификатор задачи.
       name : str   Название задачи (обязательное поле, уникальное).
       content : str    Содержание задачи (обязательное поле).
       period_of_execution : datetime   Период выполнения задачи.
       parent_id : uuid.UUID    Идентификатор родительской задачи.
       status : int Статус задачи (обязательное поле, значение по умолчанию = 0).
       employee_id : uuid.UUID  Идентификатор сотрудника, ответственного за задачу.
       employees : relationship Отношение "многие к одному" с таблицей Employee.
       child_task : relationship    Отношение "один ко многим" с дочерними задачами.
       parent_task : relationship   Отношение "один ко многим" с родительской задачей.
    """
    __tablename__ = 'task'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    content = Column(Text, nullable=False)
    period_of_execution = Column(TIMESTAMP(timezone=True))
    parent_id = Column(UUID(as_uuid=True), ForeignKey(
        'task.id'), nullable=True)
    status = Column(Integer, nullable=False, default=0)
    employee_id = Column(
        UUID(
            as_uuid=True),
        ForeignKey('employee.id'),
        nullable=True)

    employees = relationship("Employee", back_populates='tasks', lazy='joined')

    child_task = relationship(
        "Task",
        back_populates='parent_task',
        lazy='joined')
    parent_task = relationship(
        "Task",
        remote_side='Task.id',
        back_populates='child_task',
        foreign_keys=[parent_id],
        lazy='joined')

    def __repr__(self):
        return (f"Task(name='{self.name}', "
                f"content='{self.content}', "
                f"period_of_execution='{self.period_of_execution}', "
                f"parent_id='{self.parent_id}',"
                f"employee_id='{self.employee_id}',"
                f"status='{self.status}')")
