import aiosqlite
import pytz
from datetime import datetime

DB_NAME = 'bot.db'

#для создания таблиц при запуске
async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        #таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                current_text_status TEXT,
                current_voice_status_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        #таблица для связей "пользователь -> контакт, которому можно отвечать в ЛС"
        await db.execute('''
            CREATE TABLE IF NOT EXISTS allowed_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,         -- ID владельца статуса
                contact_id INTEGER,      -- ID друга, которому можно отвечать
                contact_name TEXT,       -- Имя друга для удобства
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.commit()

#добавление пользователя
async def add_user(user_id: int, username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)',
            (user_id, username)
        )
        await db.commit()

#обновление текстового статуса пользователя
async def update_user_text_status(user_id: int, text_status: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'UPDATE users SET current_text_status = ? WHERE user_id = ?',
            (text_status, user_id)
        )
        await db.commit()

async def get_user_status_by_username(username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        # ищем user_id и статус пользователя с таким username
        cursor = await db.execute(
            'SELECT user_id, current_text_status FROM users WHERE username = ?',
            (username,)
        )
        user_data = await cursor.fetchone()  # получаем первую найденную запись
        await cursor.close()
        return user_data  # вернет кортеж (user_id, status) или None

async def get_user_status(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            'SELECT current_text_status FROM users WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        await cursor.close()
        return result[0] if result else None

async def update_user_text_status(user_id: int, text_status: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'UPDATE users SET current_text_status = ? WHERE user_id = ?',
            (text_status, user_id)
        )
        await db.commit()