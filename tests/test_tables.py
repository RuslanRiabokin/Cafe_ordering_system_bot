import os
import pytest
import sqlite3

from Education.create_order import cursor


def test_database_file_exists(db_conn):
    """Проверяем, что файл базы данных был создан"""
    assert os.path.exists("database_test.db"), "Файл базы данных не был создан."


def test_free_tables_count(db_conn):
    """Проверяем количество свободных столиков"""
    free_tables = db_conn.get_table_names()
    assert len(free_tables) == 9, f"Ожидалось 9 свободных столиков, но найдено {len(free_tables)}."


def test_table_occupied(db_conn):
    """Проверяем, что количество свободных столиков становится 8 после занятия одного столика"""
    # Обновляем статус столика "Стіл № 9" на занятый
    db_conn.cursor.execute(
        "UPDATE Tables SET is_occupied = 1 WHERE table_name = 'Стіл № 9'"
    )
    db_conn.connection.commit()

    free_tables_after = db_conn.get_table_names()
    free_count_after = len(free_tables_after)

    assert free_count_after == 8, (
        f"Ожидалось 8 свободных столиков, но найдено {free_count_after}."
    )
    db_conn.cursor.execute(
        "UPDATE Tables SET is_occupied = 0 WHERE table_name = 'Стіл № 9'"
    )
    db_conn.connection.commit()


def test_table_does_not_exist(db_conn):
    """Проверка что такогй стол не существует"""
    db_conn.cursor.execute(
        "SELECT * FROM Tables WHERE table_name = 'Стіл № 19'"
    )
    result = db_conn.cursor.fetchone()
    assert result is None, "Ошибка: Такой стол есть."


def test_table_error_nu(db_conn):
    """Проверка, что ошибка возникает при попытке получить несуществующий столик"""
    with pytest.raises(sqlite3.DatabaseError) as excinfo:
        db_conn.cursor.execute(
            "SELECT * FROM Tables WHERE table_name = 'Стіл № 19'"
        )
        result = db_conn.cursor.fetchone()
        if result is None:
            # Эмулируем ошибку, если столик не найден
            raise sqlite3.DatabaseError("Столик не найден")
