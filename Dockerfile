# Первый этап: Сборка и тестирование
FROM python:3.11.9-slim-bullseye AS builder

# Установим необходимые пакеты для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Установим виртуальное окружение Python
RUN python -m venv /opt/venv

# Активируем виртуальное окружение
ENV PATH="/opt/venv/bin:$PATH"

# Скопируем файл requirements.txt и установим зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Скопируем весь проект в контейнер
COPY . /app

# Установим рабочую директорию
WORKDIR /app

# Установим PYTHONPATH
ENV PYTHONPATH="/app"

# Установим и запустим линтер flake8
RUN python -m pip install flake8
RUN python -m flake8 myproject

# Запустим тесты
RUN python -m pytest -v tests/test_tables.py

# Второй этап: Минимальный образ для запуска бота
FROM python:3.11.9-slim-bullseye AS final

# Скопируем виртуальное окружение из предыдущего этапа
COPY --from=builder /opt/venv /opt/venv

# Активируем виртуальное окружение
ENV PATH="/opt/venv/bin:$PATH"

# Скопируем код приложения из builder
COPY --from=builder /app /app

# Установим рабочую директорию
WORKDIR /app

# Убедитесь, что .env файл скопирован и передан во время выполнения контейнера
# (предполагается, что .env будет передан через --env-file при запуске контейнера)

# Установим команду по умолчанию для запуска бота
CMD ["python", "-m", "myproject.bot"]
