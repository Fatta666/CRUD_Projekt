# === Базовый образ с Python ===
FROM python:3.13-slim

# === Рабочая директория ===
WORKDIR /app

# === Копируем зависимости ===
COPY requirements.txt .

# === Устанавливаем зависимости ===
RUN pip install --no-cache-dir -r requirements.txt

# === Копируем весь код проекта ===
COPY . .

# === Открываем порт Flask ===
EXPOSE 5000

# === Запускаем приложение ===
CMD ["python", "app.py"]
