import sqlite3
from aiogram import Bot
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage


conn = sqlite3.connect('users.db', check_same_thread=False)

# Создаем таблицу users
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL
    )
""")
conn.commit()


class RegisterStates(StatesGroup):
    name = State()
    email = State()


bot = Bot(token='5709242582:AAEHkoXQIgJWknBqCuaTtxGkoE1nabomD8o')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет! Чтобы зарегистрироваться, пожалуйста, представьтесь.\n\nВведите ваше имя:")
    await RegisterStates.name.set()


@dp.message_handler(state=RegisterStates.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await message.reply("Отлично! Теперь введите ваш email:")

    await RegisterStates.email.set()


@dp.message_handler(state=RegisterStates.email)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text

    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, email) VALUES (?, ?)", (data['name'], data['email']))
    conn.commit()

    await message.reply("Спасибо! Вы успешно зарегистрированы.")
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
