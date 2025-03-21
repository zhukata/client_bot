import logging
import asyncio
from django.core.management.base import BaseCommand
from aiogram import Bot, Dispatcher

from bot.handlers.start import router as start_router
from bot.handlers.catalog import router as catalog_router
from bot.handlers.cart import router as cart_router
from bot.handlers.order import router as order_router
from bot.handlers.payment import router as payment_router
from bot.config import BOT_TOKEN


class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def handle(self, *args, **options):
        asyncio.run(self.start_bot())

    async def start_bot(self):
        logging.basicConfig(level=logging.INFO)

        bot = Bot(BOT_TOKEN)
        dp = Dispatcher()
        dp.include_router(start_router)
        dp.include_router(catalog_router)
        dp.include_router(cart_router)
        dp.include_router(order_router)
        dp.include_router(payment_router)

        self.stdout.write(self.style.SUCCESS("Бот запущен..."))
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
