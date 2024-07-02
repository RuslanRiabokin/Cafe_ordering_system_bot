from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from myproject.database import Database
from aiogram.exceptions import TelegramBadRequest
from typing import Optional
from aiogram import types
from contextlib import suppress





class MenuSelectionCallback(CallbackData, prefix="fabnum"):
    """Дає можливість вибрати з меню страви"""
    action: str
    id: int




def get_data_from_the_menu(category: str ):
    # Отримуємо дані з бази даних
    results = Database().getting_data_from_menu(category)

    builder = InlineKeyboardBuilder()

    for dish_id, dish_name, dish_price in results:
        builder.button(
            text=f"{dish_name} - {dish_price}",
            callback_data=MenuSelectionCallback(action="select", id=dish_id)
        )


    # Выравниваем кнопки в ряд
    builder.adjust(1)

    return builder.as_markup()


async def update_category_menu_fab(message: types.Message, category: str):
    """Виводе меню по обраній категорії"""
    await message.answer(
        f"Оберіть блюдо:",
        reply_markup=get_data_from_the_menu(category)
    )

# SELECT dish_name, dish_price, description FROM Menu WHERE id = 3;
# Виклик меню, ціну та опис з таблиці SQL

async def choice_of_dish(callback_query: types.CallbackQuery, callback_data: MenuSelectionCallback):
    """Вибір блюда з меню"""
    dish_details = Database().get_dish_details(callback_data.id)
    dish_name, dish_price, description = dish_details
    await callback_query.message.answer(
        f"Ви обрали: {dish_name}\n"
        f"Ціна: {dish_price}\n"
        f"Опис: {description}"
    )
    await callback_query.answer()