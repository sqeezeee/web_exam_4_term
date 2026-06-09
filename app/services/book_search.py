from app.extensions import db
from app.models.book import Book
from app.models.genre import Genre


def build_books_query(filters: dict):
  """
  Строим запрос списка книг с учётом параметров поиска (вариант 3).
  Пустые поля фильтра не учитываются.
  """
  query = Book.query

  title = (filters.get("title") or "").strip()
  if title:
    query = query.filter(Book.title.ilike(f"%{title}%"))

  author = (filters.get("author") or "").strip()
  if author:
    query = query.filter(Book.author.ilike(f"%{author}%"))

  genre_ids = filters.get("genre_ids") or []
  if genre_ids:
    query = query.filter(Book.genres.any(Genre.id.in_(genre_ids)))

  years = filters.get("years") or []
  if years:
    query = query.filter(Book.year.in_(years))

  pages_from = filters.get("pages_from")
  if pages_from is not None and pages_from != "":
    try:
      query = query.filter(Book.pages >= int(pages_from))
    except ValueError:
      pass

  pages_to = filters.get("pages_to")
  if pages_to is not None and pages_to != "":
    try:
      query = query.filter(Book.pages <= int(pages_to))
    except ValueError:
      pass

  # Сортировка по году выхода — сначала новые
  return query.order_by(Book.year.desc(), Book.id.desc())


def get_distinct_years():
  """Список годов издания, которые есть в базе (для мультиселекта)."""
  rows = (
    db.session.query(Book.year)
    .distinct()
    .order_by(Book.year.desc())
    .all()
  )
  return [row[0] for row in rows]


def parse_search_form(form) -> dict:
  """Собираем словарь фильтров из данных формы поиска."""
  return {
    "title": form.get("title", ""),
    "author": form.get("author", ""),
    "genre_ids": [int(g) for g in form.getlist("genre_ids") if g.isdigit()],
    "years": [int(y) for y in form.getlist("years") if y.isdigit()],
    "pages_from": form.get("pages_from", ""),
    "pages_to": form.get("pages_to", ""),
  }


def parse_search_args(args) -> dict:
  """Собираем фильтры из query-параметров URL (для пагинации)."""
  return {
    "title": args.get("title", ""),
    "author": args.get("author", ""),
    "genre_ids": [int(g) for g in args.getlist("genre_ids") if g.isdigit()],
    "years": [int(y) for y in args.getlist("years") if y.isdigit()],
    "pages_from": args.get("pages_from", ""),
    "pages_to": args.get("pages_to", ""),
  }
