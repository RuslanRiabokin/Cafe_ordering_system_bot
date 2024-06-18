import sqlite3

def create_db():
    # Определение пути к базе данных
    db_path = 'database.db'

    # Подключение к базе данных
    conn = sqlite3.connect(db_path)
    print(f"Connecting to the database: {db_path}")


    # Создание курсора
    cursor = conn.cursor()

    # Создание таблицы "Меню"
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dish_name TEXT NOT NULL,
        dish_price REAL NOT NULL,
        category TEXT NOT NULL
    )
    ''')

    # Создание таблицы "Столики"
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT NOT NULL
    )
    ''')

    # Создание таблицы "Заказы"
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_id INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY (table_id) REFERENCES Tables(id)
    )
    ''')

    # Создание таблицы "Меню заказа"
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderMenu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        menu_id INTEGER NOT NULL,
        FOREIGN KEY (order_id) REFERENCES Orders(id),
        FOREIGN KEY (menu_id) REFERENCES Menu(id)
    )
    ''')

    # Сохранение изменений
    conn.commit()

    # Закрытие соединения
    conn.close()

