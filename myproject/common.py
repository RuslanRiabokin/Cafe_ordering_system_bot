from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router()


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message, state: FSMContext):
    """Функция для выбора столиков"""
    await state.clear()

    # Создаем клавиатуру с кнопками выбора столиков
    builder = ReplyKeyboardBuilder()
    for i in range(1, 10):
        builder.add(types.KeyboardButton(text=f"Стол № {i}"))
    builder.adjust(3)

    # Отправляем сообщение с клавиатурой
    await message.answer(
        text="Выберите столик, нажав на кнопку с номером столика",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )




# Нетрудно догадаться, что следующие два хэндлера можно
# спокойно объединить в один, но для полноты картины оставим так

# default_state - это то же самое, что и StateFilter(None)
@router.message(StateFilter(None), Command(commands=["cancel"]))
@router.message(default_state, F.text.lower() == "отмена")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # Стейт сбрасывать не нужно, удалим только данные
    await state.set_data({})
    await message.answer(
        text="Нечего отменять",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command(commands=["cancel"]))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )


