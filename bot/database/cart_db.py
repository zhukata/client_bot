from asgiref.sync import sync_to_async
from django.db.models import F

from bot.database.catalog_db import get_client
from django_app.clients.models import Cart, CartItem
from bot.logging_config import logger


async def add_to_cart(user_id, product_id, quantity):
    """Добавляет товар в корзину пользователя"""
    client = await get_client(user_id)
    cart, _ = await Cart.objects.aget_or_create(client_id=client.id)

    cart_item, created = await CartItem.objects.aget_or_create(cart=cart, product_id=product_id)

    if not created:
        cart_item.quantity = F('quantity') + quantity
    else:
        cart_item.quantity = quantity

    await cart_item.asave()
    return cart_item


async def get_cart_items(user_id):
    """Получает список товаров в корзине пользователя"""
    try:
        client = await get_client(user_id)
        cart = await Cart.objects.aget(client_id=client.id)
        
        if not cart:
            return []
        
        items = await sync_to_async(list)(cart.items.select_related("product"))
        return items
    except Cart.DoesNotExist:
        logger.warning(f"Корзина для клиента с ID {user_id} не найдена.")
        return []
    except Exception as e:
        logger.error(f"Ошибка получения корзины для пользователя {user_id}: {e}")
        raise


async def remove_from_cart(cart_item_id):
    """Удаляет товар из корзины"""
    try:
        cart_item = await CartItem.objects.aget(id=cart_item_id)
        await cart_item.adelete()
        logger.info(f"Товар с ID {cart_item_id} успешно удалён из корзины.")
    except CartItem.DoesNotExist:
        logger.warning(f"Товар с ID {cart_item_id} не найден в корзине.")
    except Exception as e:
        logger.error(f"Ошибка при удалении товара с ID {cart_item_id}: {e}")
        raise


async def clear_cart(user_id: int) -> None:
    """Асинхронная очистка корзины пользователя"""
    cart_items = CartItem.objects.filter(cart__client__tg_id=user_id)

    if not await cart_items.aexists():
        logger.info(f"Корзина пользователя {user_id} уже пуста.")
        return

    try:
        deleted_count, _ = await cart_items.adelete()
        logger.info(f"Удалено {deleted_count} товаров из корзины пользователя {user_id}.")
    except Exception as e:
        logger.error(f"Ошибка при очистке корзины пользователя {user_id}: {e}")
        raise
