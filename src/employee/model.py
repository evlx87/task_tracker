import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Базовый класс для описания моделей."""
    pass


class Employee(Base):
    """
    Модель данных для представления информации о сотруднике.

    Attributes:
    -----------
    id : UUID           Уникальный идентификатор сотрудника.
    email : str         Email сотрудника.
    last_name : str     Фамилия сотрудника.
    first_name : str    Имя сотрудника.
    patronymic : str (optional) Отчество сотрудника.
    post : str (optional)       Должность сотрудника.
    tasks : relationship[Task]  Отношение с моделью Task.
    """
    __tablename__ = 'employee'

    id = Column(
        UUID(
            as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True)
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    patronymic = Column(String)
    post = Column(String)
    tasks = relationship(
        'Task',
        back_populates='employees',
        lazy='joined')

    def __repr__(self):
        """Метод возвращает строковое представление объекта Employee."""
        return (f"Employee(email='{self.email}', "
                f"last_name='{self.last_name}', "
                f"first_name='{self.first_name}', "
                f"patronymic='{self.patronymic}', "
                f"post='{self.post}')")

    def count_task(self) -> int:
        """
        Возвращает количество взятых для работы задач
        :return: количество задач
        """
        return len(self.tasks)
