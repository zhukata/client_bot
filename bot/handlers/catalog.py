import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from bot.database.cart_db import add_to_cart
from bot.logging_config import logger
from bot.database.catalog_db import (
    get_categories, get_product, get_subcategories, get_products,
    count_categories, count_subcategories, count_products,
    ITEMS_PER_PAGE
)
from bot.handlers.callback import (
    CategoryCallback, SubcategoryCallback, ProductCallback,
    AddToCartCallback, SetQuantityCallback, ConfirmAddCallback
)


router = Router()


async def generate_pagination_keyboard(items, total_count, callback_factory, page):
    """Создаёт инлайн-клавиатуру с пагинацией"""
    buttons = [
        [InlineKeyboardButton(text=item.name, callback_data=callback_factory(id=item.id, page=page).pack())]
        for item in items
    ]

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_factory(id=0, page=page - 1).pack()))
    if (page + 1) * ITEMS_PER_PAGE < total_count:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Вперёд", callback_data=callback_factory(id=0, page=page + 1).pack()))

    if nav_buttons:
        buttons.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == "🛍 Каталог")
async def catalog_handler(message: Message):
    """Отправляет список категорий"""
    logger.info("Получен запрос на отображение категорий.")
    categories = await get_categories(0, ITEMS_PER_PAGE)
    total_count = await count_categories()
    keyboard = await generate_pagination_keyboard(categories, total_count, CategoryCallback, 0)
    await message.answer("Выберите категорию:", reply_markup=keyboard)


@router.callback_query(CategoryCallback.filter())
async def category_handler(callback: CallbackQuery, callback_data: CategoryCallback):
    """Обрабатывает выбор категории и показывает подкатегории"""
    logger.info(f"Получен callback: {callback.data}")
    category_id = callback_data.id
    page = callback_data.page

    subcategories = await get_subcategories(category_id, page * ITEMS_PER_PAGE, ITEMS_PER_PAGE)
    total_count = await count_subcategories(category_id)
    keyboard = await generate_pagination_keyboard(subcategories, total_count, SubcategoryCallback, page)
    await callback.message.edit_text("Выберите подкатегорию:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(SubcategoryCallback.filter())
async def subcategory_handler(callback: CallbackQuery, callback_data: SubcategoryCallback):
    """Обрабатывает выбор подкатегории и показывает товары"""
    logger.info(f"Получен callback: {callback.data}")
    subcategory_id = callback_data.id
    page = callback_data.page

    products = await get_products(subcategory_id, page * ITEMS_PER_PAGE, ITEMS_PER_PAGE)
    total_count = await count_products(subcategory_id)
    keyboard = await generate_pagination_keyboard(products, total_count, ProductCallback, page)
    await callback.message.edit_text("Выберите товар:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ProductCallback.filter())
async def product_handler(callback: CallbackQuery, callback_data: ProductCallback):
    """Отображает информацию о товаре и кнопку 'Добавить в корзину'"""
    logger.info(f"Получен callback: {callback.data}")
    product_id = callback_data.id

    product = await get_product(product_id)
    if not product:
        await callback.answer("Товар не найден!", show_alert=True)
        return

    caption = f"<b>{product.name}</b>\n\n{product.description}\n\nЦена: {product.price} ₽"
    image_path = os.path.join("", str(product.image) or "")

    if product.image and os.path.exists(image_path):
        photo = FSInputFile(image_path)
        await callback.message.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🛒 Добавить в корзину", callback_data=AddToCartCallback(id=product_id).pack())],
                ]
            ),
            parse_mode="HTML"
        )
    else:
        await callback.message.answer("Ошибка: изображение не найдено!", parse_mode="HTML")
    await callback.answer()


@router.callback_query(AddToCartCallback.filter())
async def add_to_cart_handler(callback: CallbackQuery, callback_data: AddToCartCallback):
    """Запрашивает количество товара перед добавлением в корзину"""
    logger.info(f"Получен callback: {callback.data}")
    product_id = callback_data.id

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(i), callback_data=SetQuantityCallback(id=product_id, quantity=i).pack())]
        for i in range(1, 6)
    ])
    await callback.message.answer("Выберите количество товара:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(SetQuantityCallback.filter())
async def set_quantity_handler(callback: CallbackQuery, callback_data: SetQuantityCallback):
    """Обрабатывает выбор количества товара"""
    logger.info(f"Получен callback: {callback.data}")
    product_id = callback_data.id
    quantity = callback_data.quantity

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=ConfirmAddCallback(id=product_id, quantity=quantity).pack())],
    ])
    await callback.message.edit_text(f"Вы выбрали {quantity} шт. Добавить в корзину?", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(ConfirmAddCallback.filter())
async def confirm_add_to_cart(callback: CallbackQuery, callback_data: ConfirmAddCallback):
    """Добавляет товар в корзину и уведомляет пользователя"""
    logger.info(f"Получен callback: {callback.data}")
    product_id = callback_data.id
    quantity = callback_data.quantity

    user_id = callback.from_user.id
    try:
        await add_to_cart(user_id, product_id, quantity)
        await callback.message.edit_text("✅ Товар добавлен в корзину!")
    except Exception as e:
        logger.error(f"Ошибка добавления товара: {e}")
        await callback.message.edit_text("Ошибка добавления товара в корзину.")
    await callback.answer()
