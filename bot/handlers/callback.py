from aiogram.filters.callback_data import CallbackData


class CategoryCallback(CallbackData, prefix="category"):
    id: int
    page: int

class SubcategoryCallback(CallbackData, prefix="subcategory"):
    id: int
    page: int

class ProductCallback(CallbackData, prefix="product"):
    id: int

class AddToCartCallback(CallbackData, prefix="add_to_cart"):
    id: int

class SetQuantityCallback(CallbackData, prefix="set_quantity"):
    id: int
    quantity: int

class ConfirmAddCallback(CallbackData, prefix="confirm_add"):
    id: int
    quantity: int
