from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest

from bot.logging_config import logger
from bot.database.cart_db import get_cart_items
from bot.database.order_db import create_order


router = Router()


class OrderForm(StatesGroup):
    """Состояния формы оформления заказа"""
    full_name = State()
    phone = State()
    address = State()


@router.callback_query(F.data == "checkout")
async def start_order(callback: CallbackQuery, state: FSMContext):
    """
    Начинает оформление заказа
    
    Args:
        callback: объект callback запроса
        state: объект состояния FSM
    """
    try:
        user_id = callback.from_user.id
        cart_items = await get_cart_items(user_id)
        
        if not cart_items:
            await callback.answer("❌ Ваша корзина пуста. Добавьте товары перед оформлением заказа.", show_alert=True)
            return
            
        await callback.message.answer(
            "📝 Введите ваше ФИО:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]]
            )
        )
        await state.set_state(OrderForm.full_name)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при начале оформления заказа: {e}")
        await callback.answer("❌ Произошла ошибка. Пожалуйста, попробуйте позже.", show_alert=True)


@router.message(OrderForm.full_name)
async def process_full_name(message: Message, state: FSMContext):
    """
    Сохраняет ФИО и запрашивает телефон
    
    Args:
        message: объект сообщения
        state: объект состояния FSM
    """
    try:
        full_name = message.text.strip()
        
        if len(full_name) < 2:
            await message.answer("❌ ФИО слишком короткое. Пожалуйста, введите корректное ФИО:")
            return
            
        await state.update_data(full_name=full_name)
        await message.answer(
            "📞 Введите ваш номер телефона:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]]
            )
        )
        await state.set_state(OrderForm.phone)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке ФИО: {e}")
        await message.answer("❌ Произошла ошибка. Пожалуйста, попробуйте позже.")


@router.message(OrderForm.phone)
async def process_phone(message: Message, state: FSMContext):
    """
    Сохраняет телефон и запрашивает адрес
    
    Args:
        message: объект сообщения
        state: объект состояния FSM
    """
    try:
        phone = message.text.strip()
        
        # Простая валидация номера телефона
        if not phone.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            await message.answer("❌ Неверный формат номера телефона. Пожалуйста, введите корректный номер:")
            return
            
        await state.update_data(phone=phone)
        await message.answer(
            "📍 Введите ваш адрес доставки:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]]
            )
        )
        await state.set_state(OrderForm.address)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке телефона: {e}")
        await message.answer("❌ Произошла ошибка. Пожалуйста, попробуйте позже.")


@router.message(OrderForm.address)
async def process_address(message: Message, state: FSMContext):
    """
    Сохраняет адрес, создаёт заказ и показывает итог
    
    Args:
        message: объект сообщения
        state: объект состояния FSM
    """
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        
        full_name = data['full_name']
        phone = data['phone']
        address = message.text.strip()
        
        if len(address) < 10:
            await message.answer("❌ Адрес слишком короткий. Пожалуйста, введите корректный адрес:")
            return
            
        cart_items = await get_cart_items(user_id)
        if not cart_items:
            await message.answer("❌ Ваша корзина пуста. Добавьте товары перед оформлением заказа.")
            await state.clear()
            return
            
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        
        order = await create_order(user_id, full_name, phone, address, total_price, cart_items)
        
        text = (
            f"✅ Ваш заказ оформлен!\n\n"
            f"👤 ФИО: {full_name}\n"
            f"📞 Телефон: {phone}\n"
            f"📍 Адрес: {address}\n"
            f"💰 Сумма: {total_price} руб.\n\n"
            f"Теперь выберите способ оплаты."
        )
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💳 Оплатить", callback_data=f"pay_{order.id}")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order")]
            ]
        )
        
        await message.answer(text, reply_markup=keyboard)
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка при создании заказа: {e}")
        await message.answer("❌ Произошла ошибка при создании заказа. Пожалуйста, попробуйте позже.")
        await state.clear()


@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    """
    Отменяет оформление заказа
    
    Args:
        callback: объект callback запроса
        state: объект состояния FSM
    """
    try:
        await state.clear()
        await callback.message.answer("❌ Оформление заказа отменено")
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка при отмене заказа: {e}")
        await callback.answer("❌ Произошла ошибка. Пожалуйста, попробуйте позже.", show_alert=True)
