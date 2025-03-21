from aiogram import Bot, Router, F
from aiogram.types import (
    CallbackQuery, LabeledPrice, InlineKeyboardMarkup,
    InlineKeyboardButton, Message, PreCheckoutQuery
)
from aiogram.exceptions import TelegramBadRequest

from bot.logging_config import logger
from bot.database.cart_db import clear_cart
from bot.database.order_db import get_order
from bot.config import Y_KASSA_TOKEN, BOT_TOKEN
from bot.excel import save_order_to_excel


router: Router = Router()
bot: Bot = Bot(BOT_TOKEN)


@router.callback_query(F.data.startswith('pay_'))
async def process_payment(callback: CallbackQuery) -> None:
    """Генерация платежного инвойса"""
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} инициировал оплату.")

    try:
        order_id = int(callback.data.split("_")[1])
        order = await get_order(order_id)
        if not order:
            raise ValueError("Заказ не найден")
    except (IndexError, ValueError) as e:
        logger.error(f"Ошибка при получении заказа: {e}")
        await callback.message.answer("❌ Ошибка: заказ не найден!")
        return

    prices = [LabeledPrice(
        label=f'Подтверждение оплаты заказа  #{order.id}',
        amount=int(float(order.total_price) * 100)
    )]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", pay=True)],
            [InlineKeyboardButton(
                text="❌ Отмена", callback_data=f"cancel_pay_{order.id}")]
        ]
    )
    description = f"""Пожалуйста проверьте свои данные перед оплатой.\n
                    Оплатите {order.total_price}₽, чтобы завершить покупку."""

    try:
        await bot.send_invoice(
            chat_id=user_id,
            title=f'Оплата заказа #{order.id}',
            description=description,
            payload=str(order.id),
            provider_token=Y_KASSA_TOKEN,
            currency='rub',
            prices=prices,
            reply_markup=keyboard
        )
        logger.info(f"Инвойс для заказа {order.id} отправлен пользователю {user_id}.")
    except TelegramBadRequest as e:
        logger.error(f"Ошибка при отправке инвойса: {e}")
        await callback.message.answer("❌ Ошибка при создании платежа.")

    await callback.message.answer("Следуйте дальнейшим инструкциям для оплаты")


@router.callback_query(F.data.startswith('cancel_pay_'))
async def cancel_payment(callback: CallbackQuery) -> None:
    """Отмена оплаты пользователем"""
    logger.info(f"Пользователь {callback.from_user.id} отменил оплату.")
    await callback.message.answer("❌ Оплата отменена.")
    await callback.message.delete()


@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery) -> None:
    """Подтверждение перед оплатой"""
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)
    logger.info(f"Предварительная проверка платежа {pre_checkout_q.id} пройдена.")


@router.message(F.successful_payment)
async def process_successful_payment(message: Message) -> None:
    """Обрабатывает успешную оплату"""
    order_id = int(message.successful_payment.invoice_payload)
    user_id = message.from_user.id
    logger.info(f"Платеж за заказ {order_id} от пользователя {user_id} прошел успешно.")

    # Записываем заказ в Excel
    try:
        await save_order_to_excel(order_id)
    except Exception as e:
        logger.error(f"Ошибка при сохранении заказа {order_id} в Excel: {e}")

    # Очищаем корзину
    try:
        await clear_cart(user_id)
    except Exception as e:
        logger.error(f"Ошибка при очистке корзины: {e}")

    await message.answer(
        f"✅ Оплата заказа #{order_id} прошла успешно!\n"
        "Ваш заказ будет обработан в ближайшее время. Спасибо!"
    )
