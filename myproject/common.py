from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove
from myproject.tableKeyboard import TableKeyboard
from myproject.database import Database

router = Router()

# Ініціалізуємо об'єкт класу з зазначенням шляху до бази даних
table_keyboard = TableKeyboard()


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message, state: FSMContext):
    """Функція для вибору столиків"""
    await state.clear()

    # Створюємо клавіатуру з кнопками вибору столиків
    keyboard = table_keyboard.create_keyboard(table_names=Database().get_table_names())

    # Надсилаємо повідомлення з клавіатурою
    await message.answer(
        text="Виберіть столик, натиснувши на кнопку з номером столика",
        reply_markup=keyboard
    )


@router.message(StateFilter(None), Command(commands=["cancel"]))
@router.message(default_state, F.text.lower() == "відміна")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # Стан скидати не потрібно, видалимо тільки дані
    await state.set_data({})
    await message.answer(
        text="Нічого відміняти",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "відміна")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Дію відмінено",
        reply_markup=ReplyKeyboardRemove()
    )
