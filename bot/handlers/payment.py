import logging
from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton, Message, PreCheckoutQuery
from bot.database.cart_db import clear_cart
from bot.database.catalog_db import get_client
from bot.database.order_db import get_order
from bot.config import Y_KASSA_TOKEN, BOT_TOKEN
# from bot.utils.excel import save_order_to_excel

router = Router()
bot = Bot(BOT_TOKEN)

@router.callback_query(F.data.startswith('pay_'))
async def process_payment(callback: CallbackQuery):
    """Генерация платежного инвойса"""
    logging.info(f"Пользователь {callback.from_user.id} инициировал оплату.")

    order_id = int(callback.data.split("_")[1])
    order = await get_order(order_id)

    if not order:
        await callback.message.answer("❌ Ошибка: заказ не найден!")
        logging.error(f"Заказ {order_id} не найден.")
        return

    prices = [LabeledPrice(
        label=f'Оплата заказа #{order.id}',
        amount=int(float(order.total_price) * 100)
    )]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", pay=True)],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_pay_{order.id}")]
        ]
    )

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=f'Оплата заказа #{order.id}',
        description=f'Оплатите {order.total_price}₽, чтобы завершить покупку.',
        payload=f"{order.id}",
        provider_token=Y_KASSA_TOKEN,
        currency='rub',
        prices=prices,
        reply_markup=keyboard
    )

    logging.info(f"Инвойс для заказа {order.id} отправлен.")
    await callback.message.delete()


@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    """Подтверждение перед оплатой"""
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)
    logging.info(f"Предварительная проверка платежа {pre_checkout_q.id} пройдена.")


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    """Обрабатывает успешную оплату"""
    order_id = int(message.successful_payment.invoice_payload)
    logging.info(f"Платеж за заказ {order_id} прошел успешно.")

    
    # Записываем заказ в Excel
    # await save_order_to_excel(order_id)
    
    # удаляем товары из корзины
    await clear_cart(message.from_user.id)

    await message.answer(
        f"✅ Оплата заказа #{order_id} прошла успешно!\n"
        "Ваш заказ будет обработан в ближайшее время. Спасибо!"
    )
