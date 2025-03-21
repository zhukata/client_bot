import logging
from bot.database.catalog_db import get_client
from django_app.clients.models import Order, OrderItem


async def get_order(order_id):
    try:
        order = await Order.objects.aget(id=order_id)
        return order
    except Exception as e:
        logging.warning(f"Заказ не найден {e}")
        raise


async def create_order(user_id, full_name, phone, address, total_price, cart_items):
    """Создаёт заказ в БД"""
    client = await get_client(user_id)
    order = await Order.objects.acreate(
        client=client,
        full_name=full_name,
        phone=phone,
        address=address,
        total_price=total_price
    )

    order_items = [
        OrderItem(order=order, product=item.product, quantity=item.quantity)
        for item in cart_items
    ]
    await OrderItem.objects.abulk_create(order_items)

    return order
