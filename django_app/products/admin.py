from django.contrib import admin

from django_app.products.models import Product, Category, Subcategory


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Subcategory)
