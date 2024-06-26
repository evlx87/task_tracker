import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
dot_env = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=dot_env)
DB_NAME = os.getenv('DB_NAME')
DB_PASS = os.getenv('DB_PASSWORD')
DB_USER = os.getenv('DB_USER')
DB_HOST = os.getenv('DB_HOST')

DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@localhost/{DB_NAME}'

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Функция для получения сессии базы данных с возможностью автоматического закрытия"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db():
    """Функция для создания базы данных, если она еще не существует"""

    conn = psycopg2.connect(user=DB_USER, password=DB_PASS)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM pg_catalog.pg_database "
                    f"WHERE datname = '{DB_NAME}'")
        result = cur.fetchone()

        if result[0] == 0:
            cur.execute(f"CREATE DATABASE {DB_NAME};")
            conn.commit()

    cur.close()
    conn.close()
