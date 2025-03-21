from aiogram import F, Bot, Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

from bot.logging_config import logger
from bot.database.catalog_db import get_client, create_client
from bot.config import CHANNEL_ID, GROUP_ID

router = Router()

start_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Каталог")],
            [KeyboardButton(text="🛒 Корзина"), KeyboardButton(text="ℹ️ FAQ")]
        ],
        resize_keyboard=True
    )


@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer(
        """Доступные команды:\n/start - Зарегистрироваться или войти\n
        /help - Показать это сообщение"""
    )


@router.message(CommandStart())
async def start_command(message: Message):
    user = await get_client(message.from_user.id)
    if not user:
        user = await create_client(message.from_user.id, message.from_user.username)
        await message.answer(f"Привет, {user.username or 'пользователь'}! Вы успешно зарегистрированы.", reply_markup=start_keyboard)
    else:
        await message.answer(f"Добро пожаловать обратно, {user.username or 'пользователь'}!", reply_markup=start_keyboard)


async def check_subscription(user_id: int, bot: Bot, channel_id: str) -> bool:
    """Проверяет, подписан ли пользователь на канал"""
    try:
        chat_member = await bot.get_chat_member(channel_id, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False  # Если не получилось проверить, считаем, что не подписан


# @router.message(CommandStart())
# async def start_handler(message: Message, bot: Bot):
#     user = message.from_user

#     subscribed_channel = await check_subscription(user.id, bot, CHANNEL_ID)
#     subscribed_group = await check_subscription(user.id, bot, GROUP_ID)

#     if not subscribed_channel or not subscribed_group:
#         # Если не подписан — отправляем сообщение с кнопками подписки
#         keyboard = InlineKeyboardBuilder()
#         keyboard.button(text="Подписаться", url=f"https://t.me/{CHANNEL_ID}")
#         keyboard.button(text="Вступить в группу", url=f"https://t.me/{GROUP_ID}")
#         await message.answer(
#             "Для использования бота нужно подписаться на канал и группу:",
#             reply_markup=keyboard.as_markup()
#         )
#         return
#     else:
#         # Проверяем, есть ли пользователь в БД
#         client = await get_client(user.id)
#         if not client:
#             try:
#                 await create_client(user.id, user.username)
#                 print(f"Новый клиент {user.id} добавлен в БД")
#             except Exception as e:
#                 print(f"Ошибка записи клиента {user.id} в БД : {e}")

#         await message.answer("Привет! Добро пожаловать в наш магазин \nВыбери действие в меню.")
