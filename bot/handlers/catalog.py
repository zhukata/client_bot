import logging
import os
from aiogram.types import FSInputFile
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database import (
    get_categories, get_product, get_subcategories, get_products,
    count_categories, count_subcategories, count_products,
    ITEMS_PER_PAGE
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

router = Router()

async def generate_pagination_keyboard(items, total_count, callback_prefix, page):
    """Создает инлайн-клавиатуру с пагинацией"""
    buttons = [[InlineKeyboardButton(text=item.name, callback_data=f"{callback_prefix}_{item.id}")] for item in items]

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"{callback_prefix}_page_{page - 1}"))
    if (page + 1) * ITEMS_PER_PAGE < total_count:
        nav_buttons.append(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"{callback_prefix}_page_{page + 1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(F.text == "🛍 Каталог")
async def catalog_handler(message: types.Message):
    """Отправляет список категорий"""
    logging.info("Получен запрос на отображение категорий.")
    categories = await get_categories(0, ITEMS_PER_PAGE)
    total_count = await count_categories()
    keyboard = await generate_pagination_keyboard(categories, total_count, "category", 0)
    await message.answer("Выберите категорию:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("category_page_"))
async def category_pagination_handler(callback: types.CallbackQuery):
    """Обрабатывает переключение страниц категорий"""
    logging.info(f"Получен callback: {callback.data}")
    page = int(callback.data.split("_")[-1])
    categories = await get_categories(page * ITEMS_PER_PAGE, ITEMS_PER_PAGE)
    total_count = await count_categories()
    keyboard = await generate_pagination_keyboard(categories, total_count, "category", page)
    await callback.message.edit_text("Выберите категорию:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def category_handler(callback: types.CallbackQuery):
    """Обрабатывает выбор категории и показывает подкатегории"""
    logging.info(f"Получен callback: {callback.data}")
    category_id = int(callback.data.split("_")[1])
    subcategories = await get_subcategories(category_id, 0, ITEMS_PER_PAGE)
    total_count = await count_subcategories(category_id)
    keyboard = await generate_pagination_keyboard(subcategories, total_count, f"subcategory_{category_id}", 0)
    await callback.message.edit_text("Выберите подкатегорию:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("subcategory_page_"))
async def subcategory_pagination_handler(callback: types.CallbackQuery):
    """Обрабатывает переключение страниц подкатегорий"""
    logging.info(f"Получен callback: {callback.data}")
    parts = callback.data.split("_")
    category_id = int(parts[1])
    page = int(parts[-1])
    subcategories = await get_subcategories(category_id, page * ITEMS_PER_PAGE, ITEMS_PER_PAGE)
    total_count = await count_subcategories(category_id)
    keyboard = await generate_pagination_keyboard(subcategories, total_count, f"subcategory_{category_id}", page)
    await callback.message.edit_text("Выберите подкатегорию:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("subcategory_"))
async def subcategory_handler(callback: types.CallbackQuery):
    """Обрабатывает выбор подкатегории и показывает товары"""
    logging.info(f"Получен callback: {callback.data}")
    subcategory_id = int(callback.data.split("_")[1])
    products = await get_products(subcategory_id, 0, ITEMS_PER_PAGE)
    total_count = await count_products(subcategory_id)
    keyboard = await generate_pagination_keyboard(products, total_count, f"product_{subcategory_id}", 0)
    await callback.message.edit_text("Выберите товар:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("product_page_"))
async def product_pagination_handler(callback: types.CallbackQuery):
    """Обрабатывает переключение страниц товаров"""
    logging.info(f"Получен callback: {callback.data}")
    parts = callback.data.split("_")
    subcategory_id = int(parts[1])
    page = int(parts[-1])
    products = await get_products(subcategory_id, page * ITEMS_PER_PAGE, ITEMS_PER_PAGE)
    total_count = await count_products(subcategory_id)
    keyboard = await generate_pagination_keyboard(products, total_count, f"product_{subcategory_id}", page)
    await callback.message.edit_text("Выберите товар:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("product_"))
async def product_handler(callback: types.CallbackQuery):
    """Отображает информацию о товаре и кнопку 'Добавить в корзину'"""
    logging.info(f"Получен callback: {callback.data}")
    product_id = int(callback.data.split("_")[1])
    
    # Получаем товар из БД
    product = await get_product(product_id)
    if not product:
        logging.warning(f"Товар с ID {product_id} не найден.")
        await callback.answer("Товар не найден!", show_alert=True)
        return
    
    # Формирование описания товара
    caption = f"<b>{product.name}</b>\n\n{product.description}\n\nЦена: {product.price} ₽"
    
    # Проверка пути к изображению
    image_path = os.path(str(product.image) or "")
    logging.info(f"Изображение: {image_path}")
    
    if product.image and os.path.exists(image_path):
        photo = FSInputFile(image_path)  # Загружаем файл
        await callback.message.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🛒 Добавить в корзину", callback_data=f"add_to_cart_{product_id}")],
                    [InlineKeyboardButton(text="🔙 Назад", callback_data=f"subcategory_{product.category_id}")]
                ]
            ),
            parse_mode="HTML"
        )
    else:
        logging.error("Ошибка: изображение не найдено.")
        await callback.message.answer("Ошибка: изображение не найдено!", parse_mode="HTML")
    
    await callback.answer()

