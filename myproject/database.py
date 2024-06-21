import sqlite3


class Database():

    def __init__(self):
        self.connection = sqlite3.connect('database.db')
        self.connection.execute('PRAGMA foreign_keys = 1')
        self.connection.commit()
        self.cursor = self.connection.cursor()

    def create_db(self):

        # Створення таблиці "Меню"
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dish_name TEXT NOT NULL,
            dish_price REAL NOT NULL,
            category TEXT NOT NULL
        )
        ''')

        # Створення таблиці "Столики"
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL
        )
        ''')

        # Створення таблиці "Замовлення"
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (table_id) REFERENCES Tables(id)
        )
        ''')

        # Створення таблиці "Меню замовлення"
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS OrderMenu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_id INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES Orders(id),
            FOREIGN KEY (menu_id) REFERENCES Menu(id)
        )
        ''')

        # Збереження змін
        self.connection.commit()

        # Вставка столиків від "Стіл 1" до "Стіл 9" тільки якщо їх немає в таблиці
        table_names = [f'Стіл № {i}' for i in range(1, 10)]
        for name in table_names:
            self.cursor.execute('SELECT COUNT(*) FROM Tables WHERE table_name = ?', (name,))
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute('INSERT INTO Tables (table_name) VALUES (?)', (name,))

        # Вставка нових страв у таблицю "Меню" тільки якщо вони ще не існують
        menu_items = [
                ('Хліб', 5.0, 'Закуски'),
                ('Салат', 15.0, 'Закуски'),
                ('Суп', 25.0, 'Перші страви'),
                ('Піца', 50.0, 'Основні страви'),
                ('Чай', 10.0, 'Напої'),
                ('Кава', 15.0, 'Напої')
            ]

        existing_dishes = set()

        # Отримання існуючих страв з таблиці
        self.cursor.execute('SELECT dish_name FROM Menu')
        for row in self.cursor.fetchall():
            existing_dishes.add(row[0])

        # Додавання нових страв, якщо їх немає в таблиці
        new_dishes = [
            (name, price, category) for name, price, category in menu_items if name not in existing_dishes
            ]
        if new_dishes:
            self.cursor.executemany('INSERT INTO Menu (dish_name, dish_price, category) VALUES (?, ?, ?)', new_dishes)

        # Збереження змін
        self.connection.commit()

    def get_table_names(self):
        """Отримуємо дані з Tables з столбця table_name"""
        self.cursor.execute("SELECT table_name FROM Tables")
        rows = self.cursor.fetchall() # Отримання всіх рядків результату запиту
        return [row[0] for row in rows]


    def getting_data_from_menu(self):
        """Отримуємо дані з Menu з столбця dish_name"""


    def get_name_menu_categories(self):
        """Отримуємо з таблиці Menu назву категорій"""
        self.cursor.execute("SELECT DISTINCT category FROM Menu")
        rows = self.cursor.fetchall()
        return [row[0] for row in rows] # ['Закуски', 'Перші страви', 'Основні страви', 'Напої']
