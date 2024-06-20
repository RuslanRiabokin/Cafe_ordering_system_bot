import sqlite3
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup


class TableKeyboard:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_table_names(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM Tables")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def create_keyboard(self):
        table_names = self.get_table_names()
        keyboard = []

        # Формуємо кнопки по три в ряд
        row = []
        for index, name in enumerate(table_names):
            row.append(types.KeyboardButton(text=name))
            if (index + 1) % 3 == 0:
                keyboard.append(row)
                row = []
        if row:  # Додаємо залишені кнопки, якщо вони є
            keyboard.append(row)

        # Створюємо об'єкт клавіатури
        builder = ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True
        )
        return builder


# Тестування класу TableKeyboard
def test_table_keyboard():
    # Вкажіть шлях до вашої бази даних
    db_path = 'database.db'

    # Ініціалізуємо об'єкт класу з зазначенням шляху до бази даних
    table_keyboard = TableKeyboard(db_path=db_path)

    # Перевіряємо отримання імен столів
    table_names = table_keyboard.get_table_names()
    print("Отримані імена столів:", table_names)

    # Перевіряємо створення клавіатури
    keyboard = table_keyboard.create_keyboard()
    print("Клавіатура:", keyboard)


# Запускаємо тест
if __name__ == "__main__":
    test_table_keyboard()
