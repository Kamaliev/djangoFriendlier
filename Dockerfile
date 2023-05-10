# Используем официальный образ Python в качестве базового
FROM python:3.11

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы приложения в контейнер
COPY . /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Применяем миграции
RUN python manage.py makemigrations main && python manage.py migrate && python manage.py collectstatic


# Запускаем сервер Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
