from math import ceil
from typing import List, Optional, Tuple

from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.core.cache import cache

from django_app.clients.models import Client
from django_app.products.models import Category, Product, Subcategory
from bot.logging_config import logger


ITEMS_PER_PAGE = 3  # Количество элементов на одной странице
CACHE_TIMEOUT = 3600  # Время кэширования в секундах


class Paginator:
    """Класс для пагинации списков"""
    def __init__(self, items: List, page: int = 1, per_page: int = ITEMS_PER_PAGE):
        """
        Инициализация пагинатора
        
        Args:
            items: список элементов для пагинации
            page: текущая страница (по умолчанию 1)
            per_page: количество элементов на странице
        """
        self.items = items
        self.page = max(page, 1)  # Минимальная страница = 1
        self.per_page = per_page
        self.total_count = len(items)
        self.total_pages = ceil(self.total_count / per_page)

    def get_page_items(self) -> List:
        """Возвращает элементы текущей страницы"""
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        return self.items[start:end]

    def has_next(self) -> bool:
        """Проверяет наличие следующей страницы"""
        return self.page < self.total_pages

    def has_previous(self) -> bool:
        """Проверяет наличие предыдущей страницы"""
        return self.page > 1


async def create_client(tg_id: int, tg_username: Optional[str]) -> Client:
    """
    Создает нового клиента
    
    Args:
        tg_id: ID пользователя в Telegram
        tg_username: имя пользователя в Telegram
        
    Returns:
        Client: созданный клиент
    """
    client = await Client.objects.acreate(tg_id=tg_id, username=tg_username)
    await client.asave()
    return client


async def get_client(tg_id: int) -> Optional[Client]:
    """
    Получает клиента по ID в Telegram
    
    Args:
        tg_id: ID пользователя в Telegram
        
    Returns:
        Optional[Client]: клиент или None, если не найден
    """
    try:
        return await Client.objects.aget(tg_id=tg_id)
    except ObjectDoesNotExist:
        return None


@sync_to_async
def get_categories() -> List[Category]:
    """
    Получает список всех категорий
    
    Returns:
        List[Category]: список категорий
    """
    cache_key = 'all_categories'
    categories = cache.get(cache_key)
    
    if categories is None:
        try:
            categories = list(Category.objects.all())
            cache.set(cache_key, categories, CACHE_TIMEOUT)
            logger.info(f"Получено {len(categories)} категорий из БД")
        except Exception as e:
            logger.error(f"Ошибка при получении категорий: {e}")
            categories = []
    
    return categories


@sync_to_async
def get_subcategories(category_id: int) -> List[Subcategory]:
    """
    Получает список подкатегорий для указанной категории
    
    Args:
        category_id: ID категории
        
    Returns:
        List[Subcategory]: список подкатегорий
    """
    cache_key = f'subcategories_{category_id}'
    subcategories = cache.get(cache_key)
    
    if subcategories is None:
        try:
            subcategories = list(
                Subcategory.objects.filter(category_id=category_id)
                .select_related('category')
            )
            cache.set(cache_key, subcategories, CACHE_TIMEOUT)
            logger.info(f"Получено {len(subcategories)} подкатегорий для категории {category_id}")
        except Exception as e:
            logger.error(f"Ошибка при получении подкатегорий для категории {category_id}: {e}")
            subcategories = []
    
    return subcategories


@sync_to_async
def get_products(subcategory_id: int) -> list[Product]:
    """
    Получает все товары для подкатегории
    
    Args:
        subcategory_id: ID подкатегории
        
    Returns:
        list[Product]: список товаров
    """
    try:
        products = list(
            Product.objects.filter(category_id=subcategory_id)
            .select_related('category')
        )
        logger.info(f"Получено {len(products)} товаров для подкатегории {subcategory_id}")
        return products

    except Exception as e:
        logger.error(f"Ошибка при получении товаров: {e}")
        return []


@sync_to_async
def get_product(product_id: int) -> Optional[Product]:
    """
    Получает информацию о конкретном товаре
    
    Args:
        product_id: ID товара
        
    Returns:
        Optional[Product]: объект товара или None, если товар не найден
    """
    try:
        product = Product.objects.select_related('category').get(id=product_id)
        return product
    except ObjectDoesNotExist:
        logger.warning(f"Товар с ID {product_id} не найден")
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении товара с ID {product_id}: {e}")
        return None

