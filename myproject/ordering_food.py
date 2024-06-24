from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from myproject.simple_row import make_row_keyboard
from myproject.common import cmd_start
from myproject.database import Database


router = Router()

menu_names = Database().get_name_menu_categories()



class OrderFood(StatesGroup):
    """Замовлення їжі"""
    choosing_menu_names = State()
    choosing_menu_types = State()



@router.message(Command("menu"))
async def cmd_food(message: Message, state: FSMContext):
    # Проверяем, установлено ли состояние выбора столика
    state_data = await state.get_data()
    if "table_selected" not in state_data:
        await cmd_start(message, state)  # Вызываем функцию выбора столиков
    else:
        await message.answer(
            text="Выберите вариант меню:",
            reply_markup=make_row_keyboard(menu_names)
        )
        # Устанавливаем пользователю состояние "выбирает название"
        await state.set_state(OrderFood.choosing_menu_names)


@router.message(F.text.startswith("Стіл №"))
async def table_selected(message: Message, state: FSMContext):
    table = message.text
    await state.update_data(table_selected=table)
    await message.answer(f"Вы выбрали {table}. Теперь можете выбрать вариант меню, введя команду /menu.")
    await state.set_state(OrderFood.choosing_menu_names)


@router.message(OrderFood.choosing_menu_names, F.text.in_(menu_names))
async def food_size_menu(message: Message, state: FSMContext):
    """Функція меню"""
    user_choice = message.text  # Отримуємо вибір користувача з тексту повідомлення
    menu_types = Database().getting_data_from_menu(user_choice)
    formatted_menu_types = [f"{name} ціна: {price} грн." for name, price in menu_types]
    await message.answer(
        text=f"Вы выбрали {user_choice}. Повернутись до /menu \n" 
             f"Меню {user_choice}: {', '.join(formatted_menu_types)}",
        reply_markup=ReplyKeyboardRemove()
    )







@router.message()
async def echo(message: types.Message):
    """Обработчик всех остальных сообщений. Отправляет эхо-ответ с именем и ID пользователя."""
    await message.answer(f'Привет, {message.from_user.first_name}, твой номер id: {message.from_user.id}')
    await message.answer(f'Привет, введите команду (/start)')
