import sqlite3
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup


class TableKeyboard():

    def create_keyboard(self, table_names):
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


