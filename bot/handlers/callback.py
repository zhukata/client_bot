from aiogram.filters.callback_data import CallbackData


class CategoryCallback(CallbackData, prefix="category"):
    """Callback для категорий"""
    id: int | None = None  # None для навигации, int для выбора категории
    page: int = 1


class SubcategoryCallback(CallbackData, prefix="subcategory"):
    """Callback для подкатегорий"""
    id: int | None = None  # None для навигации, int для выбора подкатегории
    page: int = 1
    category_id: int | None = None  # ID родительской категории


class ProductCallback(CallbackData, prefix="product"):
    """Callback для товаров"""
    id: int | None = None  # None для навигации, int для выбора товара
    page: int = 1
    subcategory_id: int | None = None  # ID родительской подкатегории


class AddToCartCallback(CallbackData, prefix="add_to_cart"):
    id: int


class SetQuantityCallback(CallbackData, prefix="set_quantity"):
    id: int
    quantity: int


class ConfirmAddCallback(CallbackData, prefix="confirm_add"):
    id: int
    quantity: int


class RemoveFromCartCallback(CallbackData, prefix="remove"):
    id: int


class PaymentCallback(CallbackData, prefix="pay"):
    order_id: int

