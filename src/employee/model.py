import uuid  # Импорт модуля uuid для генерации уникальных идентификаторов

# Импорт классов Column и String из sqlalchemy для определения полей
from sqlalchemy import Column, String

# Импорт класса UUID из диалекта PostgreSQL
from sqlalchemy.dialects.postgresql import UUID

# Импорт DeclarativeBase и relationship для работы с моделями и отношениями
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Базовый класс для описания моделей."""
    pass


class Employee(Base):  # Определение модели Employee
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
    __tablename__ = 'employee'  # Имя таблицы в базе данных

    id = Column(
        UUID(
            as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid.uuid4)  # Поле id типа UUID
    # Поле email типа String, уникальное
    email = Column(String, nullable=False, unique=True)
    # Поле last_name типа String, обязательное
    last_name = Column(String, nullable=False)
    # Поле first_name типа String, обязательное
    first_name = Column(String, nullable=False)
    patronymic = Column(String)  # Поле patronymic типа String
    post = Column(String)  # Поле post типа String
    tasks = relationship(
        'Task',
        back_populates='employees',
        lazy='joined')  # Отношение с моделью Task

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