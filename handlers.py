from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import database as db  #бд

#роутер
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await db.add_user(user_id, username)
    await message.answer(
        "Привет! Я StatusWave Bot \n"
        "Я помогу тебе устанавливать крутые статусы, которые будут автоматически отвечать твоим друзьям.\n\n"
        "Пока я умею вот что:\n"
        "/set_text - Установить текстовый статус\n"
        "В разработке: /set_voice, работа в группах."
    )

@router.message(Command("set_text"))
async def cmd_set_text(message: Message):
    await message.answer("Напиши мне новый текстовый статус, который я буду отправлять твоим друзьям:")

@router.message(F.text)
async def handle_text(message: Message):
    # Если это личное сообщение боту (а не команда) - сохраняем как статус
    if message.chat.type == 'private':
        user_id = message.from_user.id
        new_status = message.text
        await db.update_user_text_status(user_id, new_status)
        await message.answer(f"Отлично! Твой текстовый статус обновлен: \"{new_status}\"")
    # Если это сообщение из группы/чата - проверяем, есть ли там упоминания
    else:
        # Проверяем, есть ли в тексте сообщения упоминания
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                    pure_username = mentioned_username[1:]  # Убираем '@'

                    # ИЩЕМ пользователя в БД по username
                    user_data = await db.get_user_status_by_username(pure_username)

                    if user_data:
                        user_id, status_text = user_data
                        # Если у пользователя есть статус - отвечаем им
                        if status_text:
                            await message.reply(
                                f"Пользователь {mentioned_username} сейчас установил статус:\n"
                                f"\"{status_text}\""
                            )
                        else:
                            await message.reply(f"{mentioned_username} еще не установил статус.")
                    else:
                        # Если не нашли в БД
                        await message.reply(f"Я не знаю пользователя {mentioned_username}. Пусть он напишет мне /start.")