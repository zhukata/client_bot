from django.contrib import admin

from django_app.clients.models import Cart, CartItem, Client, Order, OrderItem


admin.site.register(Client)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
