import sqlite3
import json
from datetime import datetime


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
            category TEXT NOT NULL,
            description TEXT NOT NULL
        )
        ''')

        # Створення таблиці "Столики"
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL,
            is_occupied BOOLEAN NOT NULL DEFAULT 0
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

        # Читання даних із файлу JSON та збереження їх у змінній menu_items
        json_file_path = 'menu_items.json'

        with open(json_file_path, 'r', encoding='utf-8') as f:
            menu_items = json.load(f)

        existing_dishes = set()

        # Отримання існуючих страв з таблиці
        self.cursor.execute('SELECT dish_name FROM Menu')
        for row in self.cursor.fetchall():
            existing_dishes.add(row[0])

        # Додавання нових страв, якщо їх немає в таблиці
        new_dishes = [
            (item['dish_name'], item['dish_price'], item['category'], item['description'])
            for item in menu_items if item['dish_name'] not in existing_dishes
        ]
        if new_dishes:
            self.cursor.executemany('INSERT INTO Menu (dish_name, dish_price, category, description) VALUES (?, ?, ?, ?)', new_dishes)

        # Збереження змін
        self.connection.commit()

    def get_table_names(self):
        """Отримуємо дані з Tables з столбця table_name"""
        self.cursor.execute("SELECT table_name FROM Tables")
        rows = self.cursor.fetchall() # Отримання всіх рядків результату запиту
        return [row[0] for row in rows]


    def getting_data_from_menu(self, category):
        """Отримуємо дані з Menu з столбця dish_name"""

        self.cursor.execute("SELECT id, dish_name, dish_price FROM Menu WHERE category = ?", (category,))
        rows = self.cursor.fetchall()
        return rows

    def get_dish_details(self, dish_id: int):
        # Виконання запиту
        self.cursor.execute("SELECT dish_name, dish_price, description FROM Menu WHERE id = ?",
                            (dish_id,))
        result = self.cursor.fetchone()

        return result


    def get_name_menu_categories(self):
        """Отримуємо з таблиці Menu назву категорій"""
        self.cursor.execute("SELECT DISTINCT category FROM Menu")
        rows = self.cursor.fetchall()
        return [row[0] for row in rows] # ['Закуски', 'Перші страви', 'Основні страви', 'Напої']

    from datetime import datetime

    def create_order(self, table_name: str):
        """Створює нове замовлення"""

        # Отримання table_id по table_name
        self.cursor.execute("SELECT id FROM Tables WHERE table_name = ?",
                            (table_name,))
        table_id = self.cursor.fetchone()[0]

        # Отримання поточної дати та часу
        order_date_time = datetime.now().strftime("%d-%m-%Y %H:%M")

        # Створення нового замовлення
        self.cursor.execute("INSERT INTO Orders (table_id, order_date, total) VALUES (?, ?, ?)",
                            (table_id, order_date_time, 0))
        self.connection.commit()
        return self.cursor.lastrowid

    def get_order_by_table(self, table_name: str):
        """Отримання існуючого замовлення для заданого столика"""
        self.cursor.execute('''
        SELECT id FROM Orders 
        WHERE table_id = (SELECT id FROM Tables WHERE table_name = ?)
        AND total = 0
        ''', (table_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None


    def confirm_selected_dish(self, order_id: int, dish_id: int):
        """Відправляє id страви та додає її в OrderMenu"""

        # Додавання вибраної страви в OrderMenu
        self.cursor.execute("INSERT INTO OrderMenu (order_id, menu_id) VALUES (?, ?)",
                            (order_id, dish_id))

        # Збереження змін
        self.connection.commit()

    def view_order(self, order_id: int):
        """Виводе сформироване замовлення"""

        # Виконання запиту для отримання страв замовлення
        self.cursor.execute('''
        SELECT Menu.dish_name, Menu.dish_price
        FROM OrderMenu
        JOIN Menu ON OrderMenu.menu_id = Menu.id
        WHERE OrderMenu.order_id = ?
        ''', (order_id,))

        # Отримання результатів запиту
        results = self.cursor.fetchall()

        # Підрахунок загальної суми
        total_sum = sum(dish_price for _, dish_price in results)

        return results, total_sum



    def delete_order(self, order_id: int):
        """Видаляє замовлення з бази даних"""
        self.cursor.execute("DELETE FROM OrderMenu WHERE order_id = ?", (order_id,))
        self.cursor.execute("DELETE FROM Orders WHERE id = ?", (order_id,))
        self.connection.commit()

    def table_free(self, table_name: str):
        """Перевіряє стан столика та оновлює його"""
        self.cursor.execute("SELECT is_occupied FROM Tables WHERE table_name = ?",
                            (table_name,))
        result = self.cursor.fetchone()

        if result is None:
            return {"status": "not_found", "message": f"Столик с именем {table_name} не найден."}

        is_occupied = result[0]

        if is_occupied == 0:
            self.cursor.execute("UPDATE Tables SET is_occupied = 1 WHERE table_name = ?",
                                (table_name,))
            self.connection.commit()
            return {"status": "free"}
        else:
            return {"status": "occupied", "message": f"{table_name} занят, виберіть другий стіл."}

    def table_occupation(self, table_name: str):
        """Скидає стан зайнятості столика на 0"""
        self.cursor.execute("UPDATE Tables SET is_occupied = 0 WHERE table_name = ?",
                            (table_name,))
        self.connection.commit()
        return f"{table_name} вільний."


Database().create_db()

