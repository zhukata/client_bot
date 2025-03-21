FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

# Создаем точку входа, запускать будем через docker-compose
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]