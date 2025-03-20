import os, logging, asyncio
from django.core.management.base import BaseCommand
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from bot.handlers.start import router as start_router
from bot.handlers.catalog import router as catalog_router


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

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

        self.stdout.write(self.style.SUCCESS("Бот запущен..."))
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
