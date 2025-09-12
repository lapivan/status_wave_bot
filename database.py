import aiosqlite

DB_NAME = 'bot.db'

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                current_text_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()
        print("✅ Таблицы созданы/проверены")

async def add_user(user_id: int, username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT OR REPLACE INTO users (user_id, username) VALUES (?, ?)',
            (user_id, username)
        )
        await db.commit()
        print(f"✅ Пользователь добавлен/обновлен: {user_id} (@{username})")

async def update_user_text_status(user_id: int, username: str, text_status: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        exists = await cursor.fetchone()
        await cursor.close()
        
        if not exists:
            await db.execute(
                'INSERT INTO users (user_id, username, current_text_status) VALUES (?, ?, ?)',
                (user_id, username, text_status)
            )
            print(f"✅ Создан пользователь {user_id} (@{username}) со статусом: {text_status}")
        else:
            await db.execute(
                'UPDATE users SET current_text_status = ?, username = ? WHERE user_id = ?',
                (text_status, username, user_id)
            )
            print(f"✅ Статус обновлен для {user_id} (@{username}): {text_status}")
        
        await db.commit()

async def get_user_status_by_username(username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            'SELECT user_id, current_text_status FROM users WHERE username = ?',
            (username,)
        )
        user_data = await cursor.fetchone()
        await cursor.close()
        print(f"🔍 Поиск по username: {username}, найдено: {user_data}")
        return user_data

async def get_user_status(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            'SELECT user_id, username, current_text_status FROM users WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        await cursor.close()
        
        if result:
            user_id, username, status = result
            print(f"🔍 Найден пользователь: ID: {user_id}, Username: {username}, Status: '{status}'")
            return status
        else:
            print(f"🔍 Пользователь {user_id} не найден в БД")
            return None

async def clear_user_status(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'UPDATE users SET current_text_status = NULL WHERE user_id = ?',
            (user_id,)
        )
        await db.commit()
        print(f"✅ Статус очищен для {user_id}")

async def debug_print_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT * FROM users')
        all_users = await cursor.fetchall()
        await cursor.close()
        print("=== DEBUG: ВСЕ ПОЛЬЗОВАТЕЛИ В БД ===")
        for user in all_users:
            print(f"ID: {user[0]}, Username: {user[1]}, Status: '{user[2]}'")
        print("===================================")