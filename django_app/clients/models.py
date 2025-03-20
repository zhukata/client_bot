from django.db import models

from django_app.products.models import Product


class Client(models.Model):
    tg_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Cart(models.Model):
    """Одна корзина на одного пользователя"""
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Корзина {self.client.username}"


class CartItem(models.Model):
    """Товары в корзине"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')  # Уникальность товара в корзине

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"


class Order(models.Model):
    """Модель заказа"""
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Заказ #{self.id} от {self.client.username}"


class OrderItem(models.Model):
    """Товары в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"
