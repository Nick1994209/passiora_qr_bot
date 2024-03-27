import logging
import os
import asyncio
import sqlite3
from datetime import datetime
import pytz

from aiogram import Dispatcher, Bot, types, Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramNetworkError

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from texts import hi_msg, check_sub_msg
from keyboards import go_kb, check_sub_kb

logging.basicConfig(level=logging.INFO)
logging.info("Bot started")

bot = Bot(token=os.getenv('TOKEN'), parse_mode="HTML")
dp = Dispatcher()
user_router = Router()
admin_router = Router()
admin_router.message.filter(F.from_user.id.in_({5812314624}))
dp.include_routers(admin_router, user_router)


def add_user_to_db(user_id):
    # Создаем соединение с базой данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Создаем таблицу, если она еще не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (user_id INTEGER PRIMARY KEY, date TEXT, telegram INTEGER, instagram INTEGER, instagram_username TEXT)''')

    # Получаем текущую дату и время в московском часовом поясе
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(moscow_tz)

    # Добавляем пользователя в базу данных
    cursor.execute("INSERT OR IGNORE INTO users (user_id, date) VALUES (?, ?)", (user_id, now.strftime('%Y-%m-%d')))

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()



@user_router.message(Command('start'))
async def admin_command(message: types.Message):
    await message.answer(hi_msg, reply_markup=go_kb)
    # добавляем пользователя в базу данных 
    add_user_to_db(message.from_user.id)


@user_router.callback_query(F.data == 'start_lottery')
async def start_lottery_cmd(callback: CallbackQuery, bot: Bot):
    await callback.message.answer(check_sub_msg, reply_markup=check_sub_kb)



@user_router.callback_query(F.data == 'check_sub')
async def check_subs(callback: CallbackQuery, bot: Bot):
    try:
        user_channel_status = await bot.get_chat_member(chat_id='@hjgkasdhkgsd', user_id=callback.from_user.id)
        if user_channel_status.status != 'left':
            pass # подписан
        else:
            pass # не подписан
    except Exception as e:
        await callback.answer(f'Ошибка: {e}')


async def main():
    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        except TelegramNetworkError as e:
            await asyncio.sleep(8)  # Задержка перед повторной попыткой

asyncio.run(main())