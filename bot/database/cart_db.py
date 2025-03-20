from asgiref.sync import sync_to_async
from django.db.models import F
from django_app.clients.models import Cart, CartItem

# @sync_to_async
# def add_to_cart(tg_id, product_id, quantity):
#     """Добавляет товар в корзину пользователя"""
#     cart, _ = Cart.objects.get_or_create(client_id=tg_id)  # Получаем корзину пользователя

#     cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
    
#     if not created:
#         cart_item.quantity = F('quantity') + quantity  # Увеличиваем количество
#     else:
#         cart_item.quantity = quantity

#     cart_item.save()


async def add_to_cart(user_id : int, product_id, quantity):
    cart = await Cart.objects.acreate(client_id=user_id)
    await cart.asave()
    cart_item = await CartItem.objects.acreate(cart=cart, product_id=product_id, quantity=quantity)
    await cart_item.asave()
    return cart_item