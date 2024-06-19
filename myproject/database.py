import sqlite3

def create_db():
    # Визначення шляху до бази даних
    db_path = 'database.db'

    # Підключення до бази даних
    conn = sqlite3.connect(db_path)
    print(f"Connecting to the database: {db_path}")

    # Створення курсора
    cursor = conn.cursor()

    # Створення таблиці "Меню"
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dish_name TEXT NOT NULL,
        dish_price REAL NOT NULL,
        category TEXT NOT NULL
    )
    ''')

    # Створення таблиці "Столики"
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT NOT NULL
    )
    ''')

    # Створення таблиці "Замовлення"
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY (table_id) REFERENCES Tables(id)
    )
    ''')

    # Створення таблиці "Меню замовлення"
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderMenu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        menu_id INTEGER NOT NULL,
        FOREIGN KEY (order_id) REFERENCES Orders(id),
        FOREIGN KEY (menu_id) REFERENCES Menu(id)
    )
    ''')

    # Збереження змін
    conn.commit()

    # Вставка столиків від "Стіл 1" до "Стіл 9" тільки якщо їх немає в таблиці
    table_names = [f'Стіл {i}' for i in range(1, 10)]
    for name in table_names:
        cursor.execute('SELECT COUNT(*) FROM Tables WHERE table_name = ?', (name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO Tables (table_name) VALUES (?)', (name,))

    # Збереження змін
    conn.commit()

    # Закриття з'єднання
    conn.close()

# Виклик функції створення бази даних
create_db()
