from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.catalog_db import Paginator
from bot.handlers.callback import CategoryCallback, ProductCallback, SubcategoryCallback


def create_list_keyboard(items, page: int, callback_class, parent_id: int = None, 
                        back_button_text: str = None, back_callback = None):
    """
    Создает универсальную клавиатуру для списка элементов с пагинацией
    
    Args:
        items: Список элементов для отображения
        page: Текущая страница
        callback_class: Класс для создания callback_data
        parent_id: ID родительского элемента (если есть)
        back_button_text: Текст кнопки возврата (если нужна)
        back_callback: Callback для кнопки возврата
    """
    paginator = Paginator(items, page)
    keyboard = InlineKeyboardBuilder()
    
    # Добавляем элементы списка
    for item in paginator.get_page_items():
        if callback_class == SubcategoryCallback:
            callback_data = callback_class(
                id=item.id,
                page=1,
                category_id=parent_id
            ).pack()
        elif callback_class == ProductCallback:
            callback_data = callback_class(
                id=item.id,
                page=1,
                subcategory_id=parent_id
            ).pack()
        else:
            callback_data = callback_class(
                id=item.id,
                page=1
            ).pack()
            
        keyboard.add(InlineKeyboardButton(
            text=item.name,
            callback_data=callback_data
        ))
    
    # Устанавливаем по одной кнопке в ряд для элементов списка
    keyboard.adjust(1)
    
    # Формируем ряд с кнопками навигации
    nav_buttons = []
    if paginator.has_previous():
        if callback_class == SubcategoryCallback:
            nav_callback = callback_class(
                id=None,
                page=paginator.page-1,
                category_id=parent_id
            ).pack()
        elif callback_class == ProductCallback:
            nav_callback = callback_class(
                id=None,
                page=paginator.page-1,
                subcategory_id=parent_id
            ).pack()
        else:
            nav_callback = callback_class(
                id=None,
                page=paginator.page-1
            ).pack()
            
        nav_buttons.append(InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=nav_callback
        ))
        
    if paginator.has_next():
        if callback_class == SubcategoryCallback:
            nav_callback = callback_class(
                id=None,
                page=paginator.page+1,
                category_id=parent_id
            ).pack()
        elif callback_class == ProductCallback:
            nav_callback = callback_class(
                id=None,
                page=paginator.page+1,
                subcategory_id=parent_id
            ).pack()
        else:
            nav_callback = callback_class(
                id=None,
                page=paginator.page+1
            ).pack()
            
        nav_buttons.append(InlineKeyboardButton(
            text="Вперед ▶️",
            callback_data=nav_callback
        ))
    
    # Добавляем кнопки навигации в один ряд
    if nav_buttons:
        keyboard.row(*nav_buttons)
    
    # Добавляем кнопку возврата к предыдущему меню, если нужно
    if back_button_text and back_callback:
        keyboard.row(InlineKeyboardButton(
            text=back_button_text,
            callback_data=back_callback
        ))
    
    return keyboard.as_markup()


def get_category_keyboard(categories, page: int):
    """Создает клавиатуру для списка категорий"""
    return create_list_keyboard(
        items=categories,
        page=page,
        callback_class=CategoryCallback
    )


def get_subcategory_keyboard(subcategories, page: int, category_id: int):
    """Создает клавиатуру для списка подкатегорий"""
    return create_list_keyboard(
        items=subcategories,
        page=page,
        callback_class=SubcategoryCallback,
        parent_id=category_id,
        back_button_text="↩️ К категориям",
        back_callback=CategoryCallback(id=None, page=1).pack()
    )


def get_product_keyboard(products, page: int, subcategory_id: int, category_id: int = None):
    """Создает клавиатуру для списка товаров"""
    return create_list_keyboard(
        items=products,
        page=page,
        callback_class=ProductCallback,
        parent_id=subcategory_id,
        back_button_text="↩️ К подкатегориям",
        back_callback=SubcategoryCallback(id=None, page=1, category_id=category_id).pack()
    )

