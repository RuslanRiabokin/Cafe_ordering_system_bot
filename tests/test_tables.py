import os

def test_database_file_exists(db_conn):
    # Проверяем, что файл базы данных был создан
    assert os.path.exists("database_test.db"), "Файл базы данных не был создан."


def test_free_tables_count(db_conn):
    # Проверяем количество свободных столиков
    free_tables = db_conn.get_table_names()
    assert len(free_tables) == 9, f"Ожидалось 9 свободных столиков, но найдено {len(free_tables)}."
