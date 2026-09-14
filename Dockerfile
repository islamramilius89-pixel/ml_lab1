# Базовый образ
FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Устанавливаем зависимости для psycopg2
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение и актуальную обученную модель
COPY . .
RUN test -f model.pkl

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]