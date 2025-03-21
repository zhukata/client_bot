from aiogram import Router,  F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from bot.logging_config import logger
from bot.database.cart_db import get_cart_items
from bot.database.order_db import create_order


router = Router()


class OrderForm(StatesGroup):
    full_name = State()
    phone = State()
    address = State()


@router.callback_query(F.data == "checkout")
async def start_order(callback: CallbackQuery, state: FSMContext):
    """Начинает оформление заказа"""
    await callback.message.answer("📝 Введите ваше ФИО:")
    await state.set_state(OrderForm.full_name)
    await callback.answer()


@router.message(OrderForm.full_name)
async def process_full_name(message: Message, state: FSMContext):
    """Сохраняет ФИО и запрашивает телефон"""
    await state.update_data(full_name=message.text)
    await message.answer("📞 Введите ваш номер телефона:")
    await state.set_state(OrderForm.phone)


@router.message(OrderForm.phone)
async def process_phone(message: Message, state: FSMContext):
    """Сохраняет телефон и запрашивает адрес"""
    await state.update_data(phone=message.text)
    await message.answer("📍 Введите ваш адрес доставки:")
    await state.set_state(OrderForm.address)


@router.message(OrderForm.address)
async def process_address(message: Message, state: FSMContext):
    """Сохраняет адрес, создаёт заказ и показывает итог"""
    user_id = message.from_user.id
    data = await state.get_data()

    logger.info(f"Полученные данные state: {data}")

    full_name = data['full_name']
    phone = data['phone']
    address = message.text

    cart_items = await get_cart_items(user_id)
    logger.info(f"Товары в корзине пользователя {user_id}: {cart_items}")

    if not cart_items:
        await message.answer("❌ Ваша корзина пуста. Добавьте товары перед оформлением заказа.")
        await state.clear()
        return

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    logger.info(f"Общая сумма заказа: {total_price} руб.")

    order = await create_order(user_id, full_name, phone, address, total_price, cart_items)
    logger.info(f"Создан заказ: {order}")

    text = f"✅ Ваш заказ оформлен!\n\n" \
           f"👤 ФИО: {full_name}\n" \
           f"📞 Телефон: {phone}\n" \
           f"📍 Адрес: {address}\n" \
           f"💰 Сумма: {total_price} руб.\n\n" \
           f"Теперь выберите способ оплаты."

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", callback_data=f"pay_{order.id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
        ]
    )

    await message.answer(text, reply_markup=keyboard)
    await state.clear()
