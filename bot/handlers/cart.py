import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from bot.database.cart_db import get_cart_items, remove_from_cart
from bot.handlers.callback import RemoveFromCartCallback


router = Router()
logging.basicConfig(level=logging.INFO)


@router.message(F.text == "🛒 Корзина")
async def cart_handler(message: Message):
    """Отправляет список товаров в корзине"""
    user_id = message.from_user.id
    try:
        cart_items = await get_cart_items(user_id)
        logging.info(f"Корзина пользователя {user_id}: {cart_items}")
    except Exception as e:
        logging.error(f"Ошибка получения корзины для пользователя {user_id}: {e}")
        await message.answer("Произошла ошибка при получении корзины. Попробуйте позже.")
        return

    # Если корзина пуста
    if not cart_items:
        await message.answer("🛒 Ваша корзина пуста.")
        return

    # Формируем текст и клавиатуру
    text = "🛍 Ваши товары в корзине:\n\n"
    buttons = []

    for item in cart_items:
        # Формируем callback_data и логируем его
        callback_data = RemoveFromCartCallback(id=item.id).pack()
        logging.info(f"Сформирован callback_data для товара: {callback_data}")

        text += f"📌 {item.product.name} — {item.quantity} шт.\n"
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ Удалить {item.product.name}",
                callback_data=callback_data
            )
        ])

    # Добавляем кнопку "Оформить заказ"
    buttons.append([
        InlineKeyboardButton(
            text="✅ Оформить заказ",
            callback_data="checkout"
        )
    ])

    # Создаём клавиатуру
    try:
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(text, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Ошибка при создании клавиатуры для пользователя {user_id}: {e}")
        await message.answer("Произошла ошибка при отображении корзины.")


@router.callback_query(lambda c: c.data.startswith("remove:"))
async def remove_from_cart_handler(callback: CallbackQuery):
    try:
        cart_item_id = int(callback.data.split(":")[1])
        logging.info(f"Удаляем товар с ID: {cart_item_id}")
        await remove_from_cart(cart_item_id)
        await callback.answer("❌ Товар удалён.")
    except Exception as e:
        logging.warning(f"Ошибка при удалении: {e}")
        await callback.answer("Ошибка удаления.", show_alert=True)
