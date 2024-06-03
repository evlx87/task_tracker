import psycopg2

from src.db_connect import DB_NAME, DB_USER, DB_PASS, DB_HOST

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST
)
cursor = conn.cursor()


def fill_database():
    with open('test_data.sql', 'r', encoding='utf-8') as file:
        sql_script = file.read()

    try:
        cursor.execute(sql_script)
        conn.commit()
        print("Тестовые данные успешно добавлены в базу данных.")
    except Exception as e:
        print(f"Ошибка заполнения базы данных: {e}")


if __name__ == '__main__':
    fill_database()

conn.close()
