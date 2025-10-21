import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from dotenv import load_dotenv

from src.aggr_alg import save_in_json

load_dotenv()

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=os.getenv("BOT_TOKEN"))
# Диспетчер
dp = Dispatcher()

date_from = "2022-09-01T00:00:00"
date_to = "2022-12-31T23:59:00"

# Хэндлер на команду /start
@dp.message(Command("start"))
async def main_menu(message: types.Message):
    filters = [
        ("1. получить даты по умолчанию", "default"),
        ("2. изменить интервал дат по умолчанию", "change"),
    ]

    # Показываем список
    text = ("Добрый день! Я ваш личный помощник в просмотре информации о зарплатах сотрудников компании."
            f"\n\nИнтервал дат по умолчанию:\n{date_from} - {date_to}\n\n"
            "Что вас интересует:\n\n") + "\n".join([f[0] for f in filters])
    await message.answer(text)

class DateStates(StatesGroup):
    waiting_date_from = State()
    waiting_date_to = State()

async def show_filter_options(message: types.Message):
    kb = [
        [types.KeyboardButton(text="по дням"),
        types.KeyboardButton(text="по месяцам"),
        types.KeyboardButton(text="по годам"),
        types.KeyboardButton(text="вернуться назад"),]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        selective=True,
    )
    await message.answer(
        "Выберите, как хотите отфильтровать:",
        reply_markup=keyboard
    )

# хэндлер для получения дат, отсортированных по умолчанию: 2022-09-01T00:00:00 - 2022-12-31T23:59:00,
@dp.message(F.text.regexp(r'^[12]$'))
async def handle_menu_selection(message: types.Message, state: FSMContext):
    choice = message.text

    if choice == "1":
        await show_filter_options(message)
    elif choice == "2":
        await start_date_change(message, state)

@dp.message(F.text == "2")
async def start_date_change(message: types.Message, state: FSMContext):
    await message.answer("Введите начальную дату (YYYY-MM-DDTHH:MM:SS):")
    await state.set_state(DateStates.waiting_date_from)

@dp.message(DateStates.waiting_date_from)
async def process_date_from(message: types.Message, state: FSMContext):
    await state.update_data(date_from=message.text)
    await message.answer("Введите конечную дату:")
    await state.set_state(DateStates.waiting_date_to)

@dp.message(DateStates.waiting_date_to)
async def process_date_to(message: types.Message, state: FSMContext):
    global date_from, date_to

    data = await state.get_data()
    date_from = data['date_from']  # Меняем глобальную переменную
    date_to = message.text  # Меняем глобальную переменную

    await message.answer(f"✅ Даты обновлены!\n{date_from} - {date_to}")
    await state.clear()
    await main_menu(message)  # Возвращаем в главное меню

async def date_filter(message: types.Message, group_type: str):
    kb = [
        [
            types.KeyboardButton(text="по дням"),
            types.KeyboardButton(text="по месяцам"),
            types.KeyboardButton(text="по годам"),
            types.KeyboardButton(text="вернуться назад"),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        selective=True,
    )
    data_result = save_in_json(date_from, date_to, group_type)

    await message.reply(f"📊 Результат:\n{data_result}")
    await message.answer(
        "выберите, как хотите отфильтровать",
        reply_markup=keyboard
    )

# хэндлер для получения дат, отсортированных по дням
@dp.message(F.text.lower() == "по дням")
async def sort_to_days(message: types.Message):
    await date_filter(message, "day")

# хэндлер для получения дат, отсортированных по месяцам
@dp.message(F.text.lower() == "по месяцам")
async def sort_to_month(message: types.Message):
    await date_filter(message, "month")

# хэндлер для получения дат, отсортированных по годам
@dp.message(F.text.lower() == "по годам")
async def sort_to_year(message: types.Message):
    await date_filter(message, "year")

@dp.message(F.text.lower() == "вернуться назад")
async def go_to_main(message: types.Message):
    await message.answer("Возвращаю в главное меню...")
    await main_menu(message)
