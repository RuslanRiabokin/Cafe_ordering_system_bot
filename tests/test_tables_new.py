import os
import pytest
from myproject.exceptions import TableNotFoundException, TableOccupiedException



def test_database_file_exists(db_conn):
    """Перевіряємо, що файл бази даних було створено"""
    assert os.path.exists("database_test.db"), "Файл бази даних не було створено."


def test_free_tables_count(db_conn):
    """Перевіряємо кількість вільних столиків"""
    free_tables = db_conn.get_table_names()
    assert len(free_tables) == 9, f"Очікувалось 9 вільних столиків, але знайдено {len(free_tables)}."


def test_table_not_found(db_conn):
    """Перевірка, що викликається виняток, якщо столик не знайдено"""
    with pytest.raises(TableNotFoundException):
        db_conn.table_occupation("Неіснуючий столик")


def test_table_free_occupied(db_conn):
    """Перевірка, що вільний столик оновлюється на зайнятий"""
    table_name = db_conn.get_table_names()[0]
    result = db_conn.table_occupation(table_name)
    assert result == "free", "Очікувалося, що столик буде вільним і його стан оновиться"
    with pytest.raises(TableOccupiedException):
        db_conn.table_occupation(table_name)

def test_table_already_occupied(db_conn):
    """Перевірка, що викликається виняток, якщо столик вже зайнятий"""
    table_name = db_conn.get_table_names()[0]
    db_conn.table_occupation(table_name)
    with pytest.raises(TableOccupiedException):
        db_conn.table_occupation(table_name)


