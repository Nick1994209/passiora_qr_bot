import logging
import os
import asyncio
import sqlite3
from datetime import datetime
import pytz
import instaloader

from aiogram import Dispatcher, Bot, types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

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

class Ig_Sub(StatesGroup):
    ig_sub = State()


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

def check_ig_sub(ig_username):
    # Создание экземпляра класса Instaloader
    bot = instaloader.Instaloader()
    bot.login(user=os.getenv('IG_LOGIN'), passwd=os.getenv('IG_PASSWORD'))

    # Получение имени текущего пользователя
    username = bot.context.username

    # Загрузка профиля текущего пользователя
    profile = instaloader.Profile.from_username(bot.context, username)

    # Получение списка подписчиков текущего пользователя
    followers = [follower.username for follower in profile.get_followers()]

    # Проверка наличия ig_username в списке подписчиков
    return ig_username in followers

@user_router.message(Command('start'))
async def admin_command(message: types.Message):
    await message.answer(hi_msg, reply_markup=go_kb)
    # добавляем пользователя в базу данных 
    add_user_to_db(message.from_user.id)


@user_router.callback_query(F.data == 'start_lottery')
async def start_lottery_cmd(callback: CallbackQuery, bot: Bot):
    await callback.message.answer(check_sub_msg, reply_markup=check_sub_kb)


@user_router.callback_query(F.data == 'check_sub')
async def check_subs(callback: CallbackQuery, bot: Bot, state: FSMContext):
    tg_status = "❌"
    try:
        user_channel_status = await bot.get_chat_member(chat_id='@passiora', user_id=callback.from_user.id)
        if user_channel_status.status != 'left':
            tg_status = "✅"
        else:
            tg_status = "❌"
    except Exception as e:
        await callback.answer(f'Ошибка: {e}')
    await callback.message.answer(f'Подписка в телеграме: {tg_status}\nА чтобы проверить подписку в инстаграме напиши свой никнейм:')
    await state.set_state(Ig_Sub.ig_sub)

@user_router.message(StateFilter(Ig_Sub.ig_sub))
async def check_subs(message: types.Message, bot: Bot, state: FSMContext):
    await message.answer('Дай мне пару секунд на проверку подписки в инстаграме...')
    await state.update_data(ig_username=message.text.lower())
    user_data = await state.get_data()
    if check_ig_sub(user_data["ig_username"]):
        ig_status = "✅"
    else:
        ig_status = "❌"
    await message.answer(f'Подписка в инстаграме: {ig_status}')
    await message.answer('Отлично, мы сообщим результаты конкурса 1 мая.\n\nА пока следите за нашими соцсетями ;)')
    # Сброс состояния и сохранённых данных у пользователя
    await state.clear()





async def main():
    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        except TelegramNetworkError as e:
            await asyncio.sleep(8)  # Задержка перед повторной попыткой

asyncio.run(main())