import pytest
import os
from myproject.database import Database

@pytest.fixture(scope='session', autouse=True)
def db_conn():
    # Создаём экземпляр Database
    db = Database("database_test.db")
    db.create_db()  # Создаём структуру базы данных

    # Передаём экземпляр Database в тесты
    yield db

    # Закрываем соединение и очищаем базу данных после завершения всех тестов
    db.connection.close()

    # Удаляем файл базы данных
    if os.path.exists("database_test.db"):
        os.remove("database_test.db")

@pytest.fixture(scope='session', autouse=True)
def check_file_cleanup():
    # Проверяем удаление файла после завершения всех тестов
    yield
    assert not os.path.exists("database_test.db"), "Файл базы данных не был удалён."
