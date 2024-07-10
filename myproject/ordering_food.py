from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from myproject.simple_row import make_row_keyboard
from myproject.common import cmd_start
from myproject.database import Database
from myproject.menu_selection_callback import update_category_menu_fab, choice_of_dish, MenuSelectionCallback
from aiogram.filters.callback_data import CallbackData


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
async def display_menu_by_category(message: Message, state: FSMContext):
    state_data = await state.get_data()
    state_data["category_selected"] = message.text
    await state.update_data(state_data)
    user_choice = message.text  # Отримуємо вибір користувача з тексту повідомлення
    await update_category_menu_fab(message, user_choice)



@router.callback_query(MenuSelectionCallback.filter(F.action == "back_to_menu"))
async def handle_back_to_menu(callback_query: types.CallbackQuery, state: FSMContext):
    """Повернення до вибору страв"""
    state_data = await state.get_data()
    await update_category_menu_fab(callback_query.message, state_data["category_selected"])
    await callback_query.answer()


@router.callback_query(MenuSelectionCallback.filter(F.action == "confirm"))
async def confirm_choice_dish(callback_query: types.CallbackQuery, state: FSMContext):
    """Додає  блюда до замовлення"""
    state_data = await state.get_data()
    db = Database()
    table_name = state_data["table_selected"]

    # Перевірка існуючого замовлення
    order_id = state_data.get("order_id")
    if not order_id:
        order_id = db.get_order_by_table(table_name)
        if not order_id:
            # Якщо замовлення немає, створюємо нове
            order_id = db.create_order(table_name)
        state_data["order_id"] = order_id
        await state.update_data(state_data)

    # Отримання ID страви з callback_data
    dish_id = int(callback_query.data.split(":")[2])

    # Підтвердження вибору страви
    db.confirm_selected_dish(order_id, dish_id)

    await callback_query.answer("Страву додано до замовлення!")


@router.callback_query(MenuSelectionCallback.filter())
async def handle_dish_callback(callback_query: types.CallbackQuery, callback_data: MenuSelectionCallback, state: FSMContext):
    state_data = await state.get_data()
    await choice_of_dish(callback_query, callback_data)


@router.message()
async def echo(message: types.Message):
    """Обработчик всех остальных сообщений. Отправляет эхо-ответ с именем и ID пользователя."""
    await message.answer(f'Привет, {message.from_user.first_name}, твой номер id: {message.from_user.id}')
    await message.answer(f'Привет, введите команду (/start)')
