import pandas as pd
import asyncio
import os
import logging

from django_app.clients.models import Order


EXCEL_FILE = "orders.xlsx"

async def save_order_to_excel(order_id: int) -> None:
    """
    Асинхронно получает данные заказа из базы данных и записывает их в Excel.
    :param order_id: ID заказа
    """
    try:
        # Асинхронный запрос к базе данных для получения заказа
        order = await Order.objects.aget(id=order_id)

        if not order:
            logging.warning(f"Заказ с ID {order_id} не найден.")
            return

        # Подготовка данных для записи
        data = {
            "ID заказа": [order.id],
            "ФИО": [order.full_name],
            "Телефон": [order.phone],
            "Адрес": [order.address],
            "Сумма": [order.total_price],
            "Дата": [order.created_at.strftime("%Y-%m-%d %H:%M")],
        }

        df = pd.DataFrame(data)
        file_exists = os.path.exists(EXCEL_FILE)

        # Функция синхронной записи данных в файл
        def write_to_excel():
            with open(EXCEL_FILE, mode="a", encoding="utf-8-sig") as f:
                df.to_csv(f, header=not file_exists, index=False, encoding="utf-8-sig")

        # Асинхронный запуск синхронной операции через asyncio.to_thread
        await asyncio.to_thread(write_to_excel)
        logging.info(f"Заказ {order_id} успешно записан в {EXCEL_FILE}.")
    except Exception as e:
        logging.error(f"Ошибка при сохранении заказа {order_id} в Excel: {e}")
