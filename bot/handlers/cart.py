from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from bot.logging_config import logger
from bot.database.cart_db import get_cart_items, remove_from_cart
from bot.handlers.callback import RemoveFromCartCallback


router = Router()


@router.message(F.text == "🛒 Корзина")
async def cart_handler(message: Message):
    """Отправляет список товаров в корзине"""
    user_id = message.from_user.id
    try:
        cart_items = await get_cart_items(user_id)
        logger.info(f"Корзина пользователя {user_id}: {cart_items}")
    except Exception as e:
        logger.error(f"Ошибка получения корзины для пользователя {user_id}: {e}")
        await message.answer("Произошла ошибка при получении корзины. Попробуйте позже.")
        return

    if not cart_items:
        await message.answer("🛒 Ваша корзина пуста.")
        return

    text = "🛍 Ваши товары в корзине:\n\n"
    buttons = []

    for item in cart_items:
        callback_data = RemoveFromCartCallback(id=item.id).pack()
        logger.info(f"Сформирован callback_data для товара: {callback_data}")

        text += f"📌 {item.product.name} — {item.quantity} шт.\n"
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ Удалить {item.product.name}",
                callback_data=callback_data
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="✅ Оформить заказ",
            callback_data="checkout"
        )
    ])

    try:
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка при создании клавиатуры для пользователя {user_id}: {e}")
        await message.answer("Произошла ошибка при отображении корзины.")


@router.callback_query(lambda c: c.data.startswith("remove:"))
async def remove_from_cart_handler(callback: CallbackQuery):
    try:
        cart_item_id = int(callback.data.split(":")[1])
        logger.info(f"Удаляем товар с ID: {cart_item_id}")
        await remove_from_cart(cart_item_id)
        await callback.answer("❌ Товар удалён.")
    except Exception as e:
        logger.warning(f"Ошибка при удалении: {e}")
        await callback.answer("Ошибка удаления.", show_alert=True)
