from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message, state: FSMContext):
    """Функція для вибору столиків"""
    await state.clear()

    # Створюємо клавіатуру з кнопками вибору столиків
    builder = ReplyKeyboardBuilder()
    for i in range(1, 10):
        builder.add(types.KeyboardButton(text=f"Стіл № {i}"))
    builder.adjust(3)

    # Відправляємо повідомлення з клавіатурою
    await message.answer(
        text="Виберіть столик, натиснувши на кнопку з номером столика",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )




# Не важко здогадатися, що наступні два хендлери можна
# спокійно об'єднати в один, але для повноти картини залишимо так

# default_state - це те ж саме, що і StateFilter(None)
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
