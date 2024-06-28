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
    # Получаем данные из базы данных
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
