from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from myproject.simple_row import make_row_keyboard
from myproject.common import cmd_start
from myproject.database import Database
from myproject.menu_selection_callback import (update_category_menu_fab, choice_of_dish,
                                               MenuSelectionCallback)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from myproject.exceptions import TableNotFoundException, TableOccupiedException


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
    """Вибір столика, перевірка чі вільний"""
    table = message.text
    db = Database()

    try:
        # Перевірка стану столика
        status = db.table_occupation(table)

        if status == "free":
            # Якщо столик вільний і тепер помічений як зайнятий
            await state.update_data(table_selected=table)
            await message.answer(f"Ви вибрали {table}. "
                                 f"Тепер можна обрати меню, ввівши команду /menu.",
                                 reply_markup=ReplyKeyboardRemove())
            await state.set_state(OrderFood.choosing_menu_names)

    except TableNotFoundException:
        # Якщо не знайдено столика, вивести повідомлення
        await message.answer("Стіл не знайдено")
    except TableOccupiedException:
        # Якщо стіл вже зайнятий, вивести повідомлення
        await message.answer("Стіл вже зайнятий")


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


@router.callback_query(MenuSelectionCallback.filter(F.action == "occupied"))
async def displays_formed_order(callback_query: types.CallbackQuery, state: FSMContext):
    """Виводить сформоване замовлення"""
    state_data = await state.get_data()
    db = Database()

    # Перевірка існуючого замовлення
    order_id = state_data.get("order_id")
    if not order_id:
        await callback_query.answer("Немає активних замовлень для цього столика.", show_alert=True)
        return

    # Отримання деталей замовлення та загальної суми
    order_details, total_sum = db.view_order(order_id)

    if not order_details:
        await callback_query.answer("Немає доданих страв у замовленні.", show_alert=True)
        return

    order_message = "Список страв у замовленні:\n"
    for dish_name, dish_price in order_details:
        order_message += f"{dish_name}: {dish_price} грн\n"
    order_message += f"\nЗагальна сума: {total_sum} грн"

    # Створення клавіатури з кнопкою "Сплатити замовлення"
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Сплатити замовлення",
        callback_data=MenuSelectionCallback(action="pay", id=order_id)
    )
    builder.button(
        text="Повернутися до вибору страв",
        callback_data=MenuSelectionCallback(action="back_to_menu")
    )
    builder.adjust(1)

    # Надсилання повідомлення з кнопкою Сплатити замовлення
    await callback_query.message.answer(order_message, reply_markup=builder.as_markup())
    await callback_query.answer()


@router.callback_query(MenuSelectionCallback.filter(F.action == "pay"))
async def handle_payment(callback_query: types.CallbackQuery,
                         callback_data: MenuSelectionCallback,
                         state: FSMContext):
    """Обробляє оплату замовлення та зберігає його в архів, після чого видаляє з бази даних"""
    state_data = await state.get_data()
    db = Database()

    order_id = callback_data.id
    if not order_id:
        await callback_query.answer("Немає активних замовлень для цього столика.",
                                    show_alert=True)
        return

    # Отримання імені столика зі стану
    table_name = state_data.get("table_selected")

    # Отримання деталей замовлення та загальної суми
    order_details, total_sum = db.view_order(order_id)

    # Збереження замовлення в архів
    db.archive_order(order_id, total_sum)

    # Видалення замовлення з бази даних
    db.delete_order(order_id)

    # Звільнення столика
    db.table_free(table_name)

    state_data.pop("order_id", None)
    await state.update_data(state_data)

    # Надсилання повідомлення про підтвердження оплати
    await callback_query.message.answer("Замовлення сплачено!")
    await callback_query.message.answer("Для створення нового замовлення введіть (/start)")
    await callback_query.answer()


@router.callback_query(MenuSelectionCallback.filter())
async def handle_dish_callback(
        callback_query: types.CallbackQuery,
        callback_data: MenuSelectionCallback,
        state: FSMContext
):
    await choice_of_dish(callback_query, callback_data)


@router.message()
async def echo(message: types.Message):
    """
    Обробник решти повідомлень. Відправляє луна-відповідь з ім'ям та ID користувача.
    """
    await message.answer(
        f'Привіт, {message.from_user.first_name},'
        f' твой номер id: {message.from_user.id}'
        )
    await message.answer(
        f'Привіт {message.from_user.first_name}, це бот для вибору столу та меню.'
        f'\n Щоб почати введіть(/start)'
    )
