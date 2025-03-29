from asgiref.sync import sync_to_async
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist

from bot.database.catalog_db import get_client
from django_app.clients.models import Cart, CartItem
from bot.logging_config import logger


async def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> CartItem:
    """
    Добавляет товар в корзину пользователя
    
    Args:
        user_id: ID пользователя
        product_id: ID товара
        quantity: количество товара
        
    Returns:
        CartItem: созданный или обновленный элемент корзины
    """
    try:
        client = await get_client(user_id)
        if not client:
            logger.error(f"Клиент с ID {user_id} не найден")
            raise ValueError("Клиент не найден")

        cart, created = await Cart.objects.aget_or_create(client_id=client.id)
        if created:
            logger.info(f"Создана новая корзина для клиента {user_id}")

        cart_item, created = await CartItem.objects.aget_or_create(
            cart=cart,
            product_id=product_id
        )

        if not created:
            cart_item.quantity = F('quantity') + quantity
            logger.info(f"Обновлено количество товара {product_id} в корзине {cart.id}")
        else:
            cart_item.quantity = quantity
            logger.info(f"Добавлен новый товар {product_id} в корзину {cart.id}")

        await cart_item.asave()
        return cart_item

    except Exception as e:
        logger.error(f"Ошибка при добавлении товара в корзину: {e}")
        raise


async def get_cart_items(user_id: int) -> list:
    """
    Получает список товаров в корзине пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        list: список товаров в корзине
    """
    try:
        client = await get_client(user_id)
        if not client:
            logger.warning(f"Клиент с ID {user_id} не найден")
            return []

        cart = await Cart.objects.aget(client_id=client.id)
        if not cart:
            logger.info(f"Корзина для клиента {user_id} не найдена")
            return []
        
        items = await sync_to_async(list)(cart.items.select_related("product"))
        logger.info(f"Получено {len(items)} товаров из корзины клиента {user_id}")
        return items

    except Cart.DoesNotExist:
        logger.warning(f"Корзина для клиента с ID {user_id} не найдена")
        return []
    except Exception as e:
        logger.error(f"Ошибка получения корзины для пользователя {user_id}: {e}")
        raise


async def remove_from_cart(cart_item_id: int) -> None:
    """
    Удаляет товар из корзины
    
    Args:
        cart_item_id: ID элемента корзины
    """
    try:
        cart_item = await CartItem.objects.aget(id=cart_item_id)
        cart_id = cart_item.cart_id
        await cart_item.adelete()
        logger.info(f"Товар с ID {cart_item_id} удалён из корзины {cart_id}")
    except CartItem.DoesNotExist:
        logger.warning(f"Товар с ID {cart_item_id} не найден в корзине")
    except Exception as e:
        logger.error(f"Ошибка при удалении товара с ID {cart_item_id}: {e}")
        raise


async def clear_cart(user_id: int) -> None:
    """
    Очищает корзину пользователя
    
    Args:
        user_id: ID пользователя
    """
    try:
        cart_items = CartItem.objects.filter(cart__client__tg_id=user_id)
        
        if not await cart_items.aexists():
            logger.info(f"Корзина пользователя {user_id} уже пуста")
            return

        deleted_count, _ = await cart_items.adelete()
        logger.info(f"Удалено {deleted_count} товаров из корзины пользователя {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при очистке корзины пользователя {user_id}: {e}")
        raise
