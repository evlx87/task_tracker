-- Вставляем тестовые данные для таблицы employee
INSERT INTO employee (id, email, last_name, first_name, patronymic, post)
VALUES
    ('f47ac10b-58cc-4372-a567-0e02b2c3d479', 'employee1@test.com', 'Иванов', 'Иван', 'Иванович', 'Инженер'),
    ('1f9d9f67-df24-4f7f-9f16-5a8a11cdf43e', 'employee2@test.com', 'Петров', 'Петр', NULL, 'Программист');

-- Вставляем тестовые данные для таблицы task
INSERT INTO task (id, name, content, period_of_execution, status, employee_id)
VALUES
    ('f47ac10b-58cc-4372-a567-0e02b2c3d479', 'Задание 1', 'Описание задания 1', '2023-12-01', 1, 'f47ac10b-58cc-4372-a567-0e02b2c3d479'),
    ('1f9d9f67-df24-4f7f-9f16-5a8a11cdf43e', 'Задание 2', 'Описание задания 2', '2023-12-15', 0, '1f9d9f67-df24-4f7f-9f16-5a8a11cdf43e');

