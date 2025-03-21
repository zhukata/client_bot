import logging
from asgiref.sync import sync_to_async
from django.db.models import F
from bot.database.catalog_db import get_client
from django_app.clients.models import Cart, CartItem


async def add_to_cart(user_id, product_id, quantity):
    """Добавляет товар в корзину пользователя"""
    client = await get_client(user_id)
    cart, _ = await Cart.objects.aget_or_create(client_id=client.id)  # Получаем корзину пользователя

    cart_item, created = await CartItem.objects.aget_or_create(cart=cart, product_id=product_id)
    
    if not created:
        cart_item.quantity = F('quantity') + quantity  # Увеличиваем количество
    else:
        cart_item.quantity = quantity

    await cart_item.asave()
    return cart_item


# async def add_to_cart(user_id, product_id, quantity):
#     client = await get_client(user_id)
#     client_cart = await Cart.objects.a
    
#     if client:
#         cart = await Cart.objects.acreate(client=client)

#     await cart.asave()
#     cart_item = await CartItem.objects.acreate(cart=cart, product_id=product_id, quantity=quantity)
#     await cart_item.asave()
#     return cart_item



async def get_cart_items(user_id):
    """Получает список товаров в корзине пользователя"""
    try:
        client = await get_client(user_id)  # Получаем клиента
        cart = await Cart.objects.aget(client_id=client.id)  # Получаем корзину клиента
        
        if not cart:
            return []  # Возвращаем пустой список, если корзина не найдена
        
        # Возвращаем список товаров с `select_related` для оптимизации запросов
        items = await sync_to_async(list)(cart.items.select_related("product"))
        return items
    except Cart.DoesNotExist:
        logging.warning(f"Корзина для клиента с ID {user_id} не найдена.")
        return []
    except Exception as e:
        logging.error(f"Ошибка получения корзины для пользователя {user_id}: {e}")
        raise


async def remove_from_cart(cart_item_id):
    """Удаляет товар из корзины"""
    try:
        cart_item = await CartItem.objects.aget(id=cart_item_id)
        await cart_item.adelete()
        logging.info(f"Товар с ID {cart_item_id} успешно удалён из корзины.")
    except CartItem.DoesNotExist:
        logging.warning(f"Товар с ID {cart_item_id} не найден в корзине.")
    except Exception as e:
        logging.error(f"Ошибка при удалении товара с ID {cart_item_id}: {e}")
        raise


async def clear_cart(user_id):
    """ Чистит корзину"""
    try:
        # Чистим корзину только после успешного платежа
        await CartItem.objects.filter(cart__client_id=user_id).adelete()
        logging.info(f"Корзина пользователя {user_id} успешно очищена.")
    except Exception as e:
        logging.warning(f"Ошибка очистки корзины после оплаты: {e}")
        raise