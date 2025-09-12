#main.py

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router
import database as db
import config

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties())
dp = Dispatcher(storage=storage)
dp.include_router(router)

async def main():
    try:
        bot_info = await bot.get_me()
        print(f"✅ Bot connected: @{bot_info.username}")
        
        await db.create_tables()
        print("✅ Database ready")
        
        await db.debug_print_all_users()

        print("✅ Bot started successfully! Press Ctrl+C to stop.")
        await dp.start_polling(bot)
        
    except asyncio.CancelledError:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot shutdown complete")