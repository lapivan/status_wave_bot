# database.py

import aiosqlite

DB_NAME = 'bot.db'

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                current_text_status TEXT,
                current_voice_status_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()
        print("✅ Таблицы созданы/проверены")

async def add_user(user_id: int, username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)',
            (user_id, username)
        )
        await db.commit()
        print(f"✅ Пользователь добавлен: {user_id} (@{username})")

async def update_user_text_status(user_id: int, username: str, text_status: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'UPDATE users SET current_text_status = ?, username = ? WHERE user_id = ?',
            (text_status, username, user_id)
        )
        await db.commit()
        print(f"✅ Текстовый статус обновлен для {user_id} (@{username}): {text_status}")

async def update_user_voice_status(user_id: int, username: str, voice_message_id: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'UPDATE users SET current_voice_status_id = ?, username = ? WHERE user_id = ?',
            (voice_message_id, username, user_id)
        )
        await db.commit()
        print(f"✅ Голосовой статус обновлен для {user_id} (@{username})")

async def get_user_status(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            'SELECT current_text_status FROM users WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        await cursor.close()
        return result[0] if result else None

async def get_user_voice_status(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            'SELECT current_voice_status_id FROM users WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        await cursor.close()
        return result[0] if result else None

async def get_user_status_by_username(username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            'SELECT user_id, current_text_status FROM users WHERE username = ?',
            (username,)
        )
        result = await cursor.fetchone()
        await cursor.close()
        return result

async def get_user_voice_status_by_username(username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            'SELECT user_id, current_voice_status_id FROM users WHERE username = ?',
            (username,)
        )
        result = await cursor.fetchone()
        await cursor.close()
        return result

async def clear_text_status(user_id: int):
    """Очищаем только текстовый статус"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'UPDATE users SET current_text_status = NULL WHERE user_id = ?',
            (user_id,)
        )
        await db.commit()
        print(f"✅ Текстовый статус очищен для {user_id}")

async def clear_voice_status(user_id: int):
    """Очищаем только голосовой статус"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'UPDATE users SET current_voice_status_id = NULL WHERE user_id = ?',
            (user_id,)
        )
        await db.commit()
        print(f"✅ Голосовой статус очищен для {user_id}")

async def clear_all_statuses(user_id: int):
    """Очищаем все статусы"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'UPDATE users SET current_text_status = NULL, current_voice_status_id = NULL WHERE user_id = ?',
            (user_id,)
        )
        await db.commit()
        print(f"✅ Все статусы очищены для {user_id}")

async def debug_print_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT * FROM users')
        all_users = await cursor.fetchall()
        await cursor.close()
        print("=== DEBUG: ВСЕ ПОЛЬЗОВАТЕЛИ В БД ===")
        for user in all_users:
            print(f"ID: {user[0]}, Username: {user[1]}, Text: '{user[2]}', Voice: '{user[3]}'")
        print("===================================")