"""
Скрипт начального заполнения БД: роли, жанры, тестовые пользователи и книги.
Запуск: python seed.py
"""
import base64
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models.book import Book
from app.models.cover import Cover
from app.models.genre import Genre
from app.models.role import Role
from app.models.user import User
from app.services.cover_service import compute_md5

app = create_app()

# Минимальное PNG-изображение 1x1 для демонстрационных обложек
TINY_PNG = base64.b64decode(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)

SAMPLE_BOOKS = [
  {
    "title": "Преступление и наказание",
    "description": "Роман **Ф.М. Достоевского** о студенте Родионе Раскольникове.",
    "year": 1866,
    "publisher": "Русский вестник",
    "author": "Фёдор Достоевский",
    "pages": 671,
    "genres": ["Классика", "Роман"],
  },
  {
    "title": "1984",
    "description": "Антиутопия Джорджа Оруэлла о тоталитарном обществе.",
    "year": 1949,
    "publisher": "Secker & Warburg",
    "author": "Джордж Оруэлл",
    "pages": 328,
    "genres": ["Фантастика", "Классика"],
  },
  {
    "title": "Мастер и Маргарита",
    "description": "Роман Михаила Булгакова — *одно из главных произведений* XX века.",
    "year": 1967,
    "publisher": "Художественная литература",
    "author": "Михаил Булгаков",
    "pages": 480,
    "genres": ["Классика", "Роман"],
  },
]

ROLES = [
  (Role.ADMIN, "Администратор", "Суперпользователь с полным доступом к системе"),
  (Role.MODERATOR, "Модератор", "Может редактировать книги и модерировать рецензии"),
  (Role.USER, "Пользователь", "Может оставлять рецензии на книги"),
]

GENRES = [
  "Фантастика",
  "Детектив",
  "Роман",
  "Поэзия",
  "Научная литература",
  "Приключения",
  "Классика",
  "Ужасы",
]

USERS = [
  ("admin", "admin123", "Набиуллин", "Артур", "Фанилевич", Role.ADMIN),
  ("moderator", "mod123", "Иванов", "Иван", "Иванович", Role.MODERATOR),
  ("user", "user123", "Петров", "Пётр", "Петрович", Role.USER),
]


def seed():
  with app.app_context():
    db.create_all()

    for name, desc_title, desc_text in ROLES:
      if not Role.query.filter_by(name=name).first():
        db.session.add(Role(name=name, description=desc_text))

    for genre_name in GENRES:
      if not Genre.query.filter_by(name=genre_name).first():
        db.session.add(Genre(name=genre_name))

    db.session.flush()

    for login, password, ln, fn, patronymic, role_name in USERS:
      if not User.query.filter_by(login=login).first():
        role = Role.query.filter_by(name=role_name).first()
        user = User(
          login=login,
          last_name=ln,
          first_name=fn,
          patronymic=patronymic,
          role=role,
        )
        user.set_password(password)
        db.session.add(user)

    # Демонстрационные книги (только если каталог пуст)
    if Book.query.count() == 0:
      upload_dir = Path(app.config["UPLOAD_FOLDER"])
      upload_dir.mkdir(parents=True, exist_ok=True)
      md5_hash = compute_md5(TINY_PNG)

      for item in SAMPLE_BOOKS:
        genre_objs = Genre.query.filter(Genre.name.in_(item["genres"])).all()
        book = Book(
          title=item["title"],
          description=item["description"],
          year=item["year"],
          publisher=item["publisher"],
          author=item["author"],
          pages=item["pages"],
          genres=genre_objs,
        )
        db.session.add(book)
        db.session.flush()

        cover = Cover(
          filename="temp",
          mime_type="image/png",
          md5_hash=md5_hash,
          book_id=book.id,
        )
        db.session.add(cover)
        db.session.flush()
        cover.filename = f"{cover.id}.png"
        (upload_dir / cover.filename).write_bytes(TINY_PNG)

    db.session.commit()
    print("База данных успешно заполнена.")
    print("Тестовые учётные записи:")
    print("  admin / admin123")
    print("  moderator / mod123")
    print("  user / user123")


if __name__ == "__main__":
  seed()
