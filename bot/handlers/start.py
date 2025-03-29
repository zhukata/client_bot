from aiogram import F, Bot, Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.exceptions import TelegramBadRequest
import re

from bot.logging_config import logger
from bot.database.catalog_db import get_client, create_client
from bot.config import CHANNEL_ID, GROUP_ID, CHANNEL_URL, GROUP_URL


router = Router()


start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Каталог")],
        [KeyboardButton(text="🛒 Корзина"), KeyboardButton(text="ℹ️ FAQ")]
    ],
    resize_keyboard=True
)


def format_chat_id(chat_id: str) -> str:
    """
    Форматирует ID канала/группы для корректной работы с API Telegram
    
    Args:
        chat_id: ID канала/группы
        
    Returns:
        str: отформатированный ID
    """
    # Убираем все минусы для начала
    clean_id = chat_id.replace('-', '')
    
    # Если ID не начинается с -100, добавляем его
    if not clean_id.startswith('100'):
        return f"-100{clean_id}"
    return f"-{clean_id}"


async def check_subscription(user_id: int, bot: Bot, chat_id: str) -> bool:
    """
    Проверяет, подписан ли пользователь на канал
    
    Args:
        user_id: ID пользователя
        bot: объект бота
        chat_id: id канала или группы
        
    Returns:
        bool: True если пользователь подписан, False в противном случае
    """
    try:
        formatted_chat_id = format_chat_id(chat_id)
        logger.info(f"Проверка подписки пользователя {user_id} на чат {formatted_chat_id}")
        
        chat = await bot.get_chat(formatted_chat_id)
        logger.info(f"Получена информация о чате: id={chat.id}, title={chat.title}")
        
        chat_member = await bot.get_chat_member(chat.id, user_id)
        logger.info(f"Статус подписки пользователя {user_id}: {chat_member.status}")
        
        is_subscribed = chat_member.status in ["member", "administrator", "creator"]
        logger.info(f"Результат проверки подписки: {is_subscribed}")
        
        return is_subscribed
        
    except Exception as e:
        logger.error(f"Ошибка проверки подписки на чат {chat_id}: {e}")
        return False


async def handle_subscription_check(message: Message, bot: Bot, user_id: int) -> bool:
    """
    Обрабатывает проверку подписки на канал и группу
    
    Args:
        message: объект сообщения
        bot: объект бота
        user_id: ID пользователя
        
    Returns:
        bool: True если проверка пройдена, False если нужно прервать выполнение
    """
    logger.info(f"Проверка подписки на канал {CHANNEL_ID} и группу {GROUP_ID}")

    # Проверяем подписку на канал и группу
    subscribed_channel = await check_subscription(user_id, bot, CHANNEL_ID)
    subscribed_group = await check_subscription(user_id, bot, GROUP_ID)

    logger.info(f"Результаты проверки подписки: канал={subscribed_channel}, группа={subscribed_group}")

    if not subscribed_channel or not subscribed_group:
        # Если не подписан — отправляем сообщение с кнопками подписки
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="📢 Подписаться на канал", url=CHANNEL_URL)
        keyboard.button(text="👥 Вступить в группу", url=GROUP_URL)
        keyboard.adjust(1)
        
        await message.answer(
            "Для использования бота нужно подписаться на канал и группу:",
            reply_markup=keyboard.as_markup()
        )
        logger.info(f"Пользователь {user_id} не подписан на канал или группу")
        return False
    
    return True


async def handle_user_registration(message: Message, user_id: int, username: str) -> None:
    """
    Обрабатывает регистрацию пользователя
    
    Args:
        message: объект сообщения
        user_id: ID пользователя
        username: имя пользователя
    """
    # Проверяем, есть ли пользователь в БД
    client = await get_client(user_id)
    if not client:
        try:
            client = await create_client(user_id, username)
            logger.info(f"Новый клиент {user_id} добавлен в БД")
            await message.answer(
                f"Привет, {username or 'пользователь'}! Вы успешно зарегистрированы.",
                reply_markup=start_keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка регистрации клиента {user_id}: {e}")
            await message.answer("❌ Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.")
    else:
        await message.answer(
            f"Добро пожаловать обратно, {username or 'пользователь'}!",
            reply_markup=start_keyboard
        )
        logger.info(f"Пользователь {user_id} уже зарегистрирован")


@router.message(Command('help'))
async def help_command(message: Message):
    """
    Обработчик команды /help
    
    Args:
        message: объект сообщения
    """
    try:
        await message.answer(
            "Доступные команды:\n"
            "/start - Зарегистрироваться или войти\n"
            "/help - Показать это сообщение\n\n"
            "Основные функции:\n"
            "🛍 Каталог - просмотр товаров\n"
            "🛒 Корзина - управление корзиной\n"
            "ℹ️ FAQ - часто задаваемые вопросы"
        )
        logger.info(f"Пользователь {message.from_user.id} запросил помощь")
    except Exception as e:
        logger.error(f"Ошибка при отправке справки: {e}")
        await message.answer("❌ Произошла ошибка. Пожалуйста, попробуйте позже.")


@router.message(CommandStart())
async def start_command(message: Message, bot: Bot):
    """
    Обработчик команды /start
    
    Args:
        message: объект сообщения
        bot: объект бота
    """
    try:
        user = message.from_user
        logger.info(f"Получена команда /start от пользователя {user.id}")
        
        # Проверка подписки (можно закомментировать для отладки)
        # if not await handle_subscription_check(message, bot, user.id):
        #     return
            
        # Регистрация пользователя
        await handle_user_registration(message, user.id, user.username)

    except TelegramBadRequest as e:
        logger.warning(f"Ошибка Telegram при обработке команды /start: {e}")
        await message.answer("❌ Сообщение не изменилось")
    except Exception as e:
        logger.error(f"Ошибка при обработке команды /start: {e}")
        await message.answer("❌ Произошла ошибка. Пожалуйста, попробуйте позже.")
