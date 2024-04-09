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
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from texts import hi_msg, check_sub_msg
from keyboards import go_kb, check_sub_kb, skip_sub_check_kb

logging.basicConfig(level=logging.INFO)
logging.info("Bot started")

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
user_router = Router()
admin_router = Router()
admin_router.message.filter(F.from_user.id.in_({5812314624,719426640,349455097}))
dp.include_routers(admin_router, user_router)

class Ig_Sub(StatesGroup):
    ig_sub = State()
    send_msg = State()


def add_user_to_db(user_id):
    # Создаем соединение с базой данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Создаем таблицу, если она еще не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (user_id INTEGER PRIMARY KEY, date TEXT, telegram INTEGER, instagram INTEGER, ig_username TEXT)''')

    # Получаем текущую дату и время в московском часовом поясе
    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(moscow_tz)

    # Добавляем пользователя в базу данных
    cursor.execute("INSERT OR IGNORE INTO users (user_id, date) VALUES (?, ?)", (user_id, now.strftime('%Y-%m-%d')))

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

def add_ig_username_to_db(user_id, ig_username):
    # Создаем соединение с базой данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Обновляем имя пользователя Instagram для пользователя
    cursor.execute("UPDATE users SET ig_username = ? WHERE user_id = ?", (ig_username, user_id))

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

def update_instagram_status(user_id, ig_status):
    # Создаем соединение с базой данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Обновляем статус Instagram для пользователя
    cursor.execute(f"UPDATE users SET instagram = {ig_status} WHERE user_id = ?", (user_id,))

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

def update_telegram_status(user_id, tg_status):
    # Создаем соединение с базой данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Обновляем статус Instagram для пользователя
    cursor.execute(f"UPDATE users SET telegram = {tg_status} WHERE user_id = ?", (user_id,))

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

def get_user_status_sum(user_id):
    # Создаем соединение с базой данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Получаем сумму значений столбцов telegram и instagram для пользователя
    cursor.execute("SELECT telegram + instagram AS status_sum FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    # Закрываем соединение
    conn.close()

    # Возвращаем сумму статусов, если результат не пуст, иначе возвращаем 0
    return result[0] if result else 0

def get_total_participants():
    # Создаем соединение с базой данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Выполняем запрос для получения общего количества записей, где telegram == 1 или instagram == 1 или оба значения равны 1
    cursor.execute("SELECT COUNT(*) FROM users WHERE telegram = 1 OR instagram = 1 OR (telegram = 1 AND instagram = 1)")
    total = cursor.fetchone()[0]

    # Закрываем соединение
    conn.close()

    return total

def get_list_participants():
    # Создаем соединение с базой данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Выполняем запрос для получения списка user_id, где telegram == 1 или instagram == 1 или оба значения равны 1
    cursor.execute("SELECT user_id FROM users WHERE telegram = 1 OR instagram = 1 OR (telegram = 1 AND instagram = 1)")
    participants = cursor.fetchall()

    # Закрываем соединение
    conn.close()

    # Преобразуем результат в список user_id
    user_ids = [participant[0] for participant in participants]

    return user_ids

@user_router.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer(hi_msg, reply_markup=go_kb)
    # добавляем пользователя в базу данных 
    add_user_to_db(message.from_user.id)

@user_router.callback_query(F.data == 'start_lottery')
async def start_lottery_cmd(callback: CallbackQuery, bot: Bot):
    await callback.message.answer(check_sub_msg, reply_markup=check_sub_kb)
    await callback.answer()

@user_router.callback_query(F.data == 'check_sub')
async def check_subs(callback: CallbackQuery, bot: Bot, state: FSMContext):
    tg_status = "❌"
    try:
        user_channel_status = await bot.get_chat_member(chat_id='@passiora', user_id=callback.from_user.id)
        if user_channel_status.status != 'left':
            tg_status = "✅"
            update_telegram_status(callback.from_user.id, 1)
        else:
            tg_status = "❌"
            update_telegram_status(callback.from_user.id, 0)
    except Exception as e:
        await callback.answer(f'Ошибка: {e}')
    await callback.message.answer(f'Подписка в телеграме: {tg_status}\nПроверку подписки в инстаграме проведем перед розыгрышем, пока напиши свой никнейм в инстаграме или нажми кнопку "Пропустить":', reply_markup=skip_sub_check_kb)
    await callback.answer()
    await state.set_state(Ig_Sub.ig_sub)

@user_router.callback_query(F.data == "skip_sub_check")
async def skip_sub_check(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Вы пропустили проверку подписки в Instagram.")
    await callback.answer()
    await state.clear()

@user_router.message(StateFilter(Ig_Sub.ig_sub))
async def check_subs(message: types.Message, bot: Bot, state: FSMContext):
    ig_username=message.text.lower()
    add_ig_username_to_db(message.from_user.id, ig_username)
    await message.answer('Записали ваш никнейм, подписку в инстаграме проверим перед розыгрышем. О результатах конкурса сообщим 1 мая.')
    # Сброс состояния и сохранённых данных у пользователя
    await state.clear()

@admin_router.message(Command('admin'))
async def admin_command(message: types.Message):
    total = get_total_participants()
    await message.answer(f'Всего участников в конкурсе на текущий момент: {total}')
    await message.answer(f'Для получения списка user_id участников конкурса жми команду /list')

@admin_router.message(Command('list'))
async def list_command(message: types.Message):
    list = get_list_participants()
    await message.answer(f'Список id участников конкурса: {list}')
    await message.answer(f'Если вы провели розыгрыш и мне нужно отправить сообщению победителю, используйте команду /send_msg')

@admin_router.message(Command('send_msg'))
async def send_msg_command(message: types.Message, state: FSMContext):
    await message.answer('В ответ на это сообщение пришлите мне id победителя:')
    await state.set_state(Ig_Sub.send_msg)

@admin_router.message(StateFilter(Ig_Sub.send_msg))
async def results_lottery(message: types.Message, bot: Bot, state: FSMContext):
    user_id = message.text
    try:
        await bot.send_message(user_id, 'Вы победили, свяжитесь с организаторами конкурса: @login')
        await message.answer('Сообщение победителю отправлено')
        await state.clear()
    except:
        await message.answer('Не удалось отправить сообщение победителю.\nВозможно, он заблокировал бот.\n\nВыберите нового победителя и пришлите ответным сообщением его id:')
    


async def main():
    while True:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        except TelegramNetworkError as e:
            await asyncio.sleep(8)  # Задержка перед повторной попыткой

asyncio.run(main())
