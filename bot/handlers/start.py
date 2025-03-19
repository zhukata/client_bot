from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from database import get_client, create_client

router = Router()

@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer("Доступные команды:\n/start - Зарегистрироваться или войти\n/help - Показать это сообщение")


@router.message(CommandStart())
async def start_command(message: Message):
    user = await get_client(message.from_user.id)
    if not user:
        user = await create_client(message.from_user.id)
        await message.answer(f"Привет, {user.username or 'пользователь'}! Вы успешно зарегистрированы.")
    else:
        await message.answer(f"Добро пожаловать обратно, {user.username or 'пользователь'}!")