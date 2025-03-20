from math import ceil

from asgiref.sync import sync_to_async

from django_app.clients.models import Client
from django.core.exceptions import ObjectDoesNotExist
from django_app.products.models import Category, Product, Subcategory

ITEMS_PER_PAGE = 3 # Количество элементов на одной странице


async def create_client(tg_id, tg_username):
    client = await Client.objects.acreate(tg_id=tg_id, username=tg_username)
    await client.asave()
    return client


async def get_client(tg_id):
    try:
        return await Client.objects.aget(tg_id=tg_id)
    except ObjectDoesNotExist:
        return None


# async def get_products(page: int, per_page: int):
#     """Получает список товаров с учетом пагинации"""
#     total_count = await Product.objects.acount()
#     total_pages = ceil(total_count / per_page)
    
#     offset = (page - 1) * per_page
#     products = await Product.objects.all().aoffset(offset).alimit(per_page)
    
#     return products, total_pages


async def get_product(product_id):
    try:
        return await Product.objects.aget(id=product_id)
    except ObjectDoesNotExist:
        return None


@sync_to_async
def get_categories(offset=0, limit=ITEMS_PER_PAGE):
    return list(Category.objects.all()[offset:offset + limit])


@sync_to_async
def get_subcategories(category_id, offset=0, limit=ITEMS_PER_PAGE):
    return list(Subcategory.objects.filter(category_id=category_id)[offset:offset + limit])


@sync_to_async
def get_products(subcategory_id, offset=0, limit=ITEMS_PER_PAGE):
    return list(Product.objects.filter(category=subcategory_id)[offset:offset + limit])


@sync_to_async
def count_categories():
    return Category.objects.count()


@sync_to_async
def count_subcategories(category_id):
    return Subcategory.objects.filter(category_id=category_id).count()


@sync_to_async
def count_products(subcategory_id):
    return Product.objects.filter(category=subcategory_id).count()
