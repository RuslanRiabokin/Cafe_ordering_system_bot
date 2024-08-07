import pytest
import os
from myproject.database import Database


@pytest.fixture(scope='session')
def db_conn():
    # Створюємо екземпляр Database
    db = Database("database_test.db")
    db.create_db()  # Створюємо структуру бази даних

    # Передаємо екземпляр Database у тести
    yield db

    # Закриваємо з'єднання та очищаємо базу даних після завершення всіх тестів
    db.connection.close()

    # Видаляємо файл бази даних
    if os.path.exists("database_test.db"):
        os.remove("database_test.db")


@pytest.fixture(scope='session', autouse=True)
def check_file_cleanup():
    """Перевіряємо видалення файлу після завершення всіх тестів"""
    yield
    assert not os.path.exists("database_test.db"), "Файл бази даних не видалено."
