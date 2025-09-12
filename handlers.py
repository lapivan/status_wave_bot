# handlers.py

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db

router = Router()

# Создаем состояния (статусы) для FSM
class UserState(StatesGroup):
    waiting_for_status = State()  # Состояние ожидания текста статуса

# Создаем клавиатуру с командами в ОДИН столбец
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/set_text")],
        [KeyboardButton(text="/my_status")],
        [KeyboardButton(text="/clear_status")],
        [KeyboardButton(text="/help")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери команду..."
)

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await db.add_user(user_id, username)
    
    await message.answer(
        "Привет! Я StatusWave Bot 🤖\n"
        "Я помогу тебе устанавливать крутые статусы, которые будут автоматически отвечать твоим друзьям.\n\n"
        "📋 Доступные команды:\n"
        "/set_text - Установить текстовый статус\n"
        "/my_status - Посмотреть текущий статус\n"
        "/clear_status - Удалить текущий статус\n"
        "/help - Помощь и инструкция\n\n"
        "Выбери команду или напиши ее:",
        reply_markup=main_keyboard
    )

# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "🤖 StatusWave Bot - Помощь\n\n"
        "Как работает бот:\n"
        "1. Установи статус командой /set_text\n"
        "2. Добавь меня в группу\n"
        "3. Когда тебя упомянут (@твой_ник), я автоматически отвечу твоим статусом!\n\n"
        "📋 Команды:\n"
        "/set_text - Установить новый текстовый статус\n"
        "/my_status - Посмотреть текущий статус\n"
        "/clear_status - Удалить текущий статус\n"
        "/help - Эта справка\n"
        "/start - Перезапустить бота"
    )
    await message.answer(help_text, reply_markup=main_keyboard)

# Обработчик команды /my_status
@router.message(Command("my_status"))
async def cmd_my_status(message: Message):
    user_id = message.from_user.id
    current_status = await db.get_user_status(user_id)
    if current_status:
        await message.answer(f"📝 Твой текущий статус:\n\"{current_status}\"", reply_markup=main_keyboard)
    else:
        await message.answer("❌ У тебя еще нет статуса. Используй /set_text чтобы установить его.", reply_markup=main_keyboard)

# Обработчик команды /clear_status
@router.message(Command("clear_status"))
async def cmd_clear_status(message: Message):
    user_id = message.from_user.id
    await db.update_user_text_status(user_id, None)  # Устанавливаем статус в None
    await message.answer("✅ Твой статус успешно удален!", reply_markup=main_keyboard)

# Обработчик команды /set_text - переводим в состояние ожидания статуса
@router.message(Command("set_text"))
async def cmd_set_text(message: Message, state: FSMContext):
    await message.answer(
        "Отлично! Напиши мне новый текстовый статус, который я буду отправлять твоим друзьям:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отмена")]],
            resize_keyboard=True
        )
    )
    await state.set_state(UserState.waiting_for_status)

# Обработчик состояния ожидания статуса
@router.message(UserState.waiting_for_status, F.text)
async def process_status_text(message: Message, state: FSMContext):
    if message.text.lower() in ["отмена", "❌ отмена", "cancel"]:
        await state.clear()
        await message.answer("❌ Отмена установки статуса.", reply_markup=main_keyboard)
        return
        
    user_id = message.from_user.id
    new_status = message.text
    await db.update_user_text_status(user_id, new_status)
    await state.clear()
    await message.answer(
        f"✅ Отлично! Твой текстовый статус обновлен:\n\"{new_status}\"",
        reply_markup=main_keyboard
    )

# Обработчик ЛЮБОГО текста в ЛИЧНЫХ сообщениях (не в группах!)
@router.message(F.chat.type == "private", F.text)
async def handle_private_text(message: Message):
    await message.answer(
        "🤔 Я не понимаю обычный текст. Используй команды!\n"
        "Напиши /help чтобы увидеть список команд.",
        reply_markup=main_keyboard
    )

# Обработчик для групповых сообщений с упоминаниями (ВАЖНО: этот обработчик должен быть выше!)
@router.message(F.chat.type != "private")
async def handle_group_messages(message: Message):
    # Проверяем, есть ли упоминания в сообщении
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mentioned_username = message.text[entity.offset:entity.offset + entity.length]
                pure_username = mentioned_username[1:]  # Убираем '@'
                
                # Ищем пользователя в БД по username
                user_data = await db.get_user_status_by_username(pure_username)
                if user_data:
                    user_id, status_text = user_data
                    if status_text:
                        await message.reply(
                            f"Пользователь {mentioned_username} сейчас:\n\"{status_text}\""
                        )
                    else:
                        await message.reply(f"{mentioned_username} не установил статус.")
                break  # Обрабатываем только первое упоминание