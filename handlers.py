# handlers.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db

router = Router()

class UserState(StatesGroup):
    waiting_for_status = State()
    waiting_for_voice_status = State()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📄 Текстовый статус"), KeyboardButton(text="🎤 Голосовой статус")],
        [KeyboardButton(text="📊 Мой статус"), KeyboardButton(text="🗑️ Очистить текст")],
        [KeyboardButton(text="🗑️ Очистить голос"), KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие..."
)

@router.message(F.text.in_(["📄 Текстовый статус", "🎤 Голосовой статус", "📊 Мой статус", "🗑️ Очистить текст", "🗑️ Очистить голос", "❓ Помощь"]))
async def handle_button_text(message: Message, state: FSMContext):
    text = message.text
    
    if text == "📄 Текстовый статус":
        await cmd_set_text(message, state)
    elif text == "🎤 Голосовой статус":
        await cmd_set_voice(message, state)
    elif text == "📊 Мой статус":
        await cmd_my_status(message)
    elif text == "🗑️ Очистить текст":
        await cmd_clear_text_status(message)
    elif text == "🗑️ Очистить голос":
        await cmd_clear_voice_status(message)
    elif text == "❓ Помощь":
        await cmd_help(message)

@router.message(Command("start"))
async def cmd_start(message: Message):
    print(f"🔹 Обработка /start от {message.from_user.id}")
    user_id = message.from_user.id
    username = message.from_user.username
    await db.add_user(user_id, username)
    
    await message.answer(
        "Привет! Я StatusWave Bot 🤖\n"
        "Я помогу тебе устанавливать крутые статусы (текстовые и голосовые), которые будут автоматически отвечать твоим друзьям в группах.\n\n"
        "📋 Доступные действия:\n"
        "📄 Текстовый статус\n"
        "🎤 Голосовой статус\n"
        "📊 Мой статус\n"
        "🗑️ Очистить статус\n"
        "❓ Помощь\n\n"
        "Выбери действие:",
        reply_markup=main_keyboard
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    print(f"🔹 Обработка /help от {message.from_user.id}")
    help_text = (
        "🤖 StatusWave Bot - Помощь\n\n"
        "Как работает бот:\n"
        "1. Установи статус (текстовый или голосовой)\n"
        "2. Добавь меня в группу\n"
        "3. Когда тебя упомянут (@твой_ник), я автоматически отвечу твоим статусом!\n\n"
        "📋 Команды:\n"
        "/set_text - Установить текстовый статус\n"
        "/set_voice - Установить голосовой статус\n"
        "/my_status - Посмотреть текущий статус\n"
        "/clear_status - Удалить все статусы\n"
        "/help - Эта справка\n"
        "/start - Перезапустить бота"
    )
    await message.answer(help_text, reply_markup=main_keyboard)

@router.message(Command("my_status"))
async def cmd_my_status(message: Message):
    print(f"🔹 Обработка /my_status от {message.from_user.id}")
    user_id = message.from_user.id
    
    text_status = await db.get_user_status(user_id)
    voice_status_id = await db.get_user_voice_status(user_id)
    
    if text_status or voice_status_id:
        response = "📊 Твой текущий статус:\n"
        if text_status:
            response += f"📝 Текст: \"{text_status}\"\n"
        if voice_status_id:
            response += "🎤 Голосовой: установлен\n"
        await message.answer(response, reply_markup=main_keyboard)
    else:
        await message.answer("❌ У тебя еще нет статуса.", reply_markup=main_keyboard)

# Добавляем новые команды
@router.message(Command("clear_text"))
async def cmd_clear_text_status(message: Message):
    print(f"🔹 Очистка текстового статуса от {message.from_user.id}")
    user_id = message.from_user.id
    await db.clear_text_status(user_id)
    await message.answer("✅ Текстовый статус успешно удален!", reply_markup=main_keyboard)

@router.message(Command("clear_voice"))
async def cmd_clear_voice_status(message: Message):
    print(f"🔹 Очистка голосового статуса от {message.from_user.id}")
    user_id = message.from_user.id
    await db.clear_voice_status(user_id)
    await message.answer("✅ Голосовой статус успешно удален!", reply_markup=main_keyboard)

# Обновляем старую команду очистки
@router.message(Command("clear_status"))
async def cmd_clear_all_statuses(message: Message):
    print(f"🔹 Очистка всех статусов от {message.from_user.id}")
    user_id = message.from_user.id
    await db.clear_all_statuses(user_id)
    await message.answer("✅ Все статусы успешно удалены!", reply_markup=main_keyboard)

@router.message(Command("set_text"))
async def cmd_set_text(message: Message, state: FSMContext):
    print(f"🔹 Обработка /set_text от {message.from_user.id}")
    await message.answer(
        "📝 Отлично! Напиши мне новый текстовый статус:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отмена")]],
            resize_keyboard=True
        )
    )
    await state.set_state(UserState.waiting_for_status)

@router.message(Command("set_voice"))
async def cmd_set_voice(message: Message, state: FSMContext):
    print(f"🔹 Обработка /set_voice от {message.from_user.id}")
    await message.answer(
        "🎤 Отлично! Запиши голосовое сообщение для твоего статуса:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отмена")]],
            resize_keyboard=True
        )
    )
    await state.set_state(UserState.waiting_for_voice_status)

@router.message(UserState.waiting_for_status, F.text)
async def process_status_text(message: Message, state: FSMContext):
    print(f"🔹 Обработка текстового статуса от {message.from_user.id}")
    if message.text.lower() in ["отмена", "❌ отмена", "cancel"]:
        await state.clear()
        await message.answer("❌ Отмена установки статуса.", reply_markup=main_keyboard)
        return
        
    user_id = message.from_user.id
    username = message.from_user.username
    new_status = message.text
    
    await db.update_user_text_status(user_id, username, new_status)
    await state.clear()
    await message.answer(
        f"✅ Отлично! Твой текстовый статус обновлен:\n\"{new_status}\"",
        reply_markup=main_keyboard
    )

@router.message(UserState.waiting_for_voice_status, F.voice)
async def process_voice_status(message: Message, state: FSMContext):
    print(f"🔹 Обработка голосового статуса от {message.from_user.id}")
    if message.text and message.text.lower() in ["отмена", "❌ отмена", "cancel"]:
        await state.clear()
        await message.answer("❌ Отмена установки статуса.", reply_markup=main_keyboard)
        return
        
    user_id = message.from_user.id
    username = message.from_user.username
    voice_message_id = message.voice.file_id
    
    await db.update_user_voice_status(user_id, username, voice_message_id)
    await state.clear()
    await message.answer(
        "✅ Отлично! Твой голосовой статус установлен!",
        reply_markup=main_keyboard
    )

@router.message(F.chat.type != "private")
async def handle_group_messages(message: Message):
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                pure_username = mentioned_username[1:]
                
                print(f"DEBUG: Найдено упоминание @{pure_username}")
                
                # Проверяем текстовый статус
                text_data = await db.get_user_status_by_username(pure_username)
                if text_data:
                    user_id, text_status = text_data
                    if text_status:
                        await message.reply(f"Статус {mentioned_username}:\n\"{text_status}\"")
                
                # Проверяем голосовой статус
                voice_data = await db.get_user_voice_status_by_username(pure_username)
                if voice_data:
                    user_id, voice_status_id = voice_data
                    if voice_status_id:
                        await message.reply_voice(
                            voice=voice_status_id,
                            caption=f"🎤 Голосовой статус {mentioned_username}"
                        )
                break