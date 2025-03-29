from aiogram import Router, F
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.filters import Command

from bot.logging_config import logger
from bot.config import BOT_USERNAME

router = Router()

# Словарь с часто задаваемыми вопросами и ответами
FAQ_DICT = {
    "как сделать заказ": """
1. Выберите товар в каталоге
2. Нажмите "🛒 Добавить в корзину"
3. Перейдите в корзину
4. Нажмите "💳 Оплатить"
5. Следуйте инструкциям для оплаты
    """,
    
    "способы оплаты": """
Мы принимаем следующие способы оплаты:
💳 Банковская карта
🏦 Перевод на счет
💵 Наличные при самовывозе
    """,
    
    "доставка": """
Доступные способы доставки:
🚚 Курьерская доставка
🏪 Самовывоз из магазина
📦 Почта России
    """,
    
    "возврат": """
Условия возврата:
1. Товар не был в употреблении
2. Сохранена упаковка
3. Есть чек
4. Прошло не более 14 дней
    """,
    
    "контакты": """
Наши контакты:
📞 Телефон: +7 (XXX) XXX-XX-XX
📧 Email: support@example.com
💬 Telegram: @support
    """,
    
    "работа": """
Режим работы:
Пн-Пт: 9:00 - 18:00
Сб: 10:00 - 16:00
Вс: Выходной
    """,
    
    "скидки": """
Наши скидки:
🎁 5% при первом заказе
🎁 10% при заказе от 5000₽
🎁 15% при заказе от 10000₽
    """,
    
    "гарантия": """
Гарантия на товары:
📦 14 дней на возврат
⚖️ 1 год гарантии
🛡 Защита покупателя
    """
}


@router.message(Command("faq"))
@router.message(F.text == "ℹ️ FAQ")
async def faq_command(message: Message):
    """
    Обработчик команды /faq и кнопки FAQ
    
    Args:
        message: объект сообщения
    """
    try:
        await message.answer(
            "Часто задаваемые вопросы:\n\n"
            "1. Как сделать заказ?\n"
            "2. Способы оплаты\n"
            "3. Доставка\n"
            "4. Возврат\n"
            "5. Контакты\n"
            "6. Режим работы\n"
            "7. Скидки\n"
            "8. Гарантия\n\n"
            "Для получения ответа на вопрос:\n"
            f"1. Напишите @{BOT_USERNAME} и пробел\n"
            "2. Введите интересующий вопрос\n"
            "3. Выберите подходящий вариант из списка"
        )
        logger.info(f"Пользователь {message.from_user.id} запросил FAQ")
    except Exception as e:
        logger.error(f"Ошибка при отправке FAQ: {e}")
        await message.answer("❌ Произошла ошибка. Пожалуйста, попробуйте позже.")


@router.inline_query()
async def faq_inline_query(inline_query: InlineQuery):
    """
    Обработчик инлайн-запросов для FAQ
    
    Args:
        inline_query: объект инлайн-запроса
    """
    try:
        query = inline_query.query.lower().strip()
        results = []
        
        # Если запрос пустой, показываем все вопросы
        if not query:
            for question, answer in FAQ_DICT.items():
                results.append(
                    InlineQueryResultArticle(
                        id=question,
                        title=question.capitalize(),
                        description="Нажмите, чтобы увидеть ответ",
                        input_message_content=InputTextMessageContent(
                            message_text=f"❓ {question.capitalize()}\n\n{answer}"
                        )
                    )
                )
        else:
            # Ищем совпадения в FAQ
            for question, answer in FAQ_DICT.items():
                if query in question.lower():
                    results.append(
                        InlineQueryResultArticle(
                            id=question,
                            title=question.capitalize(),
                            description="Нажмите, чтобы увидеть ответ",
                            input_message_content=InputTextMessageContent(
                                message_text=f"❓ {question.capitalize()}\n\n{answer}"
                            )
                        )
                    )
        
        # Если ничего не найдено
        if not results:
            results.append(
                InlineQueryResultArticle(
                    id="not_found",
                    title="Вопрос не найден",
                    description="Попробуйте сформулировать вопрос иначе",
                    input_message_content=InputTextMessageContent(
                        message_text=(
                            "❓ Извините, мы не нашли ответ на ваш вопрос.\n\n"
                            "Пожалуйста, попробуйте сформулировать вопрос иначе "
                            "или обратитесь в поддержку."
                        )
                    )
                )
            )
        
        await inline_query.answer(results=results, cache_time=1)
        logger.info(f"Пользователь {inline_query.from_user.id} искал: {query}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке инлайн-запроса: {e}")
        await inline_query.answer(
            results=[],
            cache_time=1,
            error_message="Произошла ошибка при поиске ответа"
        )
