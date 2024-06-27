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
    name: str
    price: Optional[float] = None




def get_data_from_the_menu(category: str ):
    # Получаем данные из базы данных
    results = Database().getting_data_from_menu(category)

    builder = InlineKeyboardBuilder()

    for dish_name, dish_price in results:
        builder.button(
            text=f"{dish_name} - {dish_price}",
            callback_data=MenuSelectionCallback(action="select",  name="", price=None)
        )


    # Выравниваем кнопки в ряд
    builder.adjust(1)

    return builder.as_markup()


async def update_num_text_fab(message: types.Message, new_value: int, category: str):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"Укажите блюдо: {new_value}",
            reply_markup=get_data_from_the_menu(category)
        )
