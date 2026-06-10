import os
from pathlib import Path

from dotenv import load_dotenv

# Загружаем переменные из .env в корне проекта
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
  SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

  SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    "sqlite:///" + str(BASE_DIR / "app.db")
  )
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  # Папка для хранения обложек книг
  UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
  MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # не больше 16 МБ на файл

  # Сколько книг показывать на одной странице списка
  BOOKS_PER_PAGE = 10
