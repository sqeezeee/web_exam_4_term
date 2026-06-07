"""
Скрипт начального заполнения БД: роли, жанры, пользователи и демо-книги с обложками.
Обложки генерируются автоматически — скачивать картинки вручную не нужно.

Запуск: python seed.py
Повторный запуск безопасен: добавятся только те книги, которых ещё нет в каталоге.
"""
import io
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app import create_app
from app.extensions import db
from app.models.book import Book
from app.models.cover import Cover
from app.models.genre import Genre
from app.models.role import Role
from app.models.user import User
from app.services.cover_service import compute_md5

app = create_app()

# Палитра фонов для обложек — у каждой книги будет свой оттенок
COVER_COLORS = [
  (44, 62, 80),
  (192, 57, 43),
  (39, 174, 96),
  (142, 68, 173),
  (41, 128, 185),
  (211, 84, 0),
  (22, 160, 133),
  (127, 140, 141),
  (52, 73, 94),
  (155, 89, 182),
  (46, 204, 113),
  (230, 126, 34),
  (52, 152, 219),
  (149, 165, 166),
  (231, 76, 60),
  (26, 188, 156),
]

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
  {
    "title": "Война и мир",
    "description": "Эпопея Льва Толстого о России эпохи наполеоновских войн.",
    "year": 1869,
    "publisher": "Русский вестник",
    "author": "Лев Толстой",
    "pages": 1225,
    "genres": ["Классика", "Роман"],
  },
  {
    "title": "Анна Каренина",
    "description": "Роман о любви, долге и русском обществе XIX века.",
    "year": 1877,
    "publisher": "Русский вестник",
    "author": "Лев Толстой",
    "pages": 864,
    "genres": ["Классика", "Роман"],
  },
  {
    "title": "Евгений Онегин",
    "description": "Роман в стихах Александра Пушкина.",
    "year": 1833,
    "publisher": "Отдельное издание",
    "author": "Александр Пушкин",
    "pages": 224,
    "genres": ["Классика", "Поэзия"],
  },
  {
    "title": "Герой нашего времени",
    "description": "Психологический роман Михаила Лермонтова.",
    "year": 1840,
    "publisher": "Библиотека для чтения",
    "author": "Михаил Лермонтов",
    "pages": 168,
    "genres": ["Классика", "Роман"],
  },
  {
    "title": "Мёртвые души",
    "description": "Поэма Николая Гоголя о помещике Чичикове.",
    "year": 1842,
    "publisher": "Московский наблюдатель",
    "author": "Николай Гоголь",
    "pages": 352,
    "genres": ["Классика", "Роман"],
  },
  {
    "title": "Идиот",
    "description": "Роман Достоевского о князе Мышкине.",
    "year": 1869,
    "publisher": "Русский вестник",
    "author": "Фёдор Достоевский",
    "pages": 640,
    "genres": ["Классика", "Роман"],
  },
  {
    "title": "Хоббит, или Туда и обратно",
    "description": "Приключенческая повесть Дж. Р. Р. Толкина.",
    "year": 1937,
    "publisher": "George Allen & Unwin",
    "author": "Дж. Р. Р. Толкин",
    "pages": 310,
    "genres": ["Фантастика", "Приключения"],
  },
  {
    "title": "Гарри Поттер и философский камень",
    "description": "Первая книга о юном волшебнике.",
    "year": 1997,
    "publisher": "Bloomsbury",
    "author": "Дж. К. Роулинг",
    "pages": 332,
    "genres": ["Фантастика", "Приключения"],
  },
  {
    "title": "Этюд в багровых тонах",
    "description": "Первое появление Шерлока Холмса.",
    "year": 1887,
    "publisher": "Beeton's Christmas Annual",
    "author": "Артур Конан Дойл",
    "pages": 176,
    "genres": ["Детектив", "Классика"],
  },
  {
    "title": "Дракула",
    "description": "Готический роман о графе Дракуле.",
    "year": 1897,
    "publisher": "Archibald Constable and Company",
    "author": "Брэм Стокер",
    "pages": 418,
    "genres": ["Ужасы", "Классика"],
  },
  {
    "title": "Франкенштейн",
    "description": "Роман Мэри Шелли о создании искусственного человека.",
    "year": 1818,
    "publisher": "Lackington, Hughes, Harding, Mavor & Jones",
    "author": "Мэри Шелли",
    "pages": 280,
    "genres": ["Ужасы", "Классика"],
  },
  {
    "title": "Солярис",
    "description": "Философская фантастика Станислава Лема.",
    "year": 1961,
    "publisher": "MON",
    "author": "Станислав Лем",
    "pages": 204,
    "genres": ["Фантастика"],
  },
  {
    "title": "Пикник на обочине",
    "description": "Роман братьев Стругацких о Зоне и сталкерах.",
    "year": 1972,
    "publisher": "Детская литература",
    "author": "Аркадий и Борис Стругацкие",
    "pages": 192,
    "genres": ["Фантастика", "Приключения"],
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


def _load_font(size: int):
  """Пробуем системный шрифт с кириллицей, иначе — встроенный."""
  candidates = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/arial.ttf",
  ]
  for path in candidates:
    if Path(path).exists():
      return ImageFont.truetype(path, size)
  return ImageFont.load_default()


def generate_cover_image(title: str, author: str, color: tuple[int, int, int]) -> bytes:
  """
  Рисуем простую обложку: цветной фон + название и автор.
  Возвращаем PNG в виде байтов для сохранения на диск.
  """
  width, height = 300, 450
  image = Image.new("RGB", (width, height), color)
  draw = ImageDraw.Draw(image)

  title_font = _load_font(22)
  author_font = _load_font(16)

  # Переносим длинное название на несколько строк
  wrapped_title = textwrap.fill(title, width=18)
  title_lines = wrapped_title.split("\n")

  y = 80
  for line in title_lines:
    bbox = draw.textbbox((0, 0), line, font=title_font)
    line_width = bbox[2] - bbox[0]
    draw.text(((width - line_width) / 2, y), line, fill="white", font=title_font)
    y += 30

  author_text = author if len(author) <= 28 else author[:25] + "..."
  bbox = draw.textbbox((0, 0), author_text, font=author_font)
  author_width = bbox[2] - bbox[0]
  draw.text(
    ((width - author_width) / 2, height - 80),
    author_text,
    fill=(230, 230, 230),
    font=author_font,
  )

  buffer = io.BytesIO()
  image.save(buffer, format="PNG")
  return buffer.getvalue()


def _save_cover_for_book(book: Book, image_data: bytes, upload_dir: Path) -> None:
  """Создаём запись обложки в БД и сохраняем файл на диск."""
  md5_hash = compute_md5(image_data)

  cover = Cover(
    filename="temp",
    mime_type="image/png",
    md5_hash=md5_hash,
    book_id=book.id,
  )
  db.session.add(cover)
  db.session.flush()
  cover.filename = f"{cover.id}.png"
  (upload_dir / cover.filename).write_bytes(image_data)


def add_book_if_missing(item: dict, upload_dir: Path, color_index: int) -> bool:
  """Добавляем книгу, если в каталоге ещё нет записи с таким названием."""
  if Book.query.filter_by(title=item["title"]).first():
    return False

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

  color = COVER_COLORS[color_index % len(COVER_COLORS)]
  image_data = generate_cover_image(item["title"], item["author"], color)
  _save_cover_for_book(book, image_data, upload_dir)
  return True


def seed():
  with app.app_context():
    db.create_all()

    for name, _desc_title, desc_text in ROLES:
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

    upload_dir = Path(app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    added = 0
    for index, item in enumerate(SAMPLE_BOOKS):
      if add_book_if_missing(item, upload_dir, index):
        added += 1

    db.session.commit()

    total = Book.query.count()
    print("База данных успешно заполнена.")
    print(f"Добавлено новых книг: {added}")
    print(f"Всего книг в каталоге: {total}")
    print("Тестовые учётные записи:")
    print("  admin / admin123")
    print("  moderator / mod123")
    print("  user / user123")


if __name__ == "__main__":
  seed()
