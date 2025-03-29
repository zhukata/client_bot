# client_bot
Телеграмм бот реализующий каталог товаров, корзину и FAQ. + Админ панель на Django. Используются Aiogram, Django, PostgreSQL, Docker.

Установка и запуск проекта через Docker Compose

1. Клонируйте репозиторий.
2. Создайте файл .env в корневой директории проекта и добавьте следующие переменные:
```
SECRET_KEY=your_secret_key
POSTGRES_DB=your_database
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

BOT_TOKEN=your_bot_token
CHANNEL_ID=your_channel_id
GROUP_ID=your_group_id
EXCEL_FILE= файл для записи эксель таблиц
Y_KASSA_TOKEN= токен для тестовых платежей юкассы
```
3. Запустите Docker Compose:
```
docker-compose up --build
```
4. Залейте тестовые данные для бд в контейнер
```
docker-compose exec db psql -U {your_postgres_user} {your_postgres_db} < dump.sql
```
Docker Compose создаст и запустит контейнеры для бота, базы данных и админки по адресу http://0.0.0.0:8000/ 
После добавления тестовых данных вы можете протестировать бота. Например по пути:
Каталог-Электроника-Ноутбук-msi- далее выбрать количество-подтвердить-перейти в корзину-оплатить

Примечание

Согласно тестовому реализовано:
1. Админ панель на Django с моделями ORM.
2. Бот подключен как отдельное джанго приложение и запускается командой python manage.py runbot 
3. Запросы к бд асинхронные.
4. Логи пишутся в файл project.log
5. Проект упакован в Docker и запускается через Docker-compose
6. Переменные окружения подключаются через .env

Основные функции бота:
1. Проверка подписки на группу и канал (закоменнтировано).
2. Каталог товаров с пагинацией.
3. Добавление и удаление товаров из корзины.
4. Тестовый платеж через ЮКасса.