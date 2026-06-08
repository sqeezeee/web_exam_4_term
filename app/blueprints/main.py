from flask import Blueprint, current_app, render_template, request

from app.extensions import db
from app.models.genre import Genre
from app.services.book_search import (
  build_books_query,
  get_distinct_years,
  parse_search_args,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
  """Главная страница со списком книг и формой поиска (вариант 3)."""
  per_page = current_app.config["BOOKS_PER_PAGE"]

  # Поиск через GET — параметры сохраняются в URL при пагинации
  filters = parse_search_args(request.args)

  query = build_books_query(filters)
  page = request.args.get("page", 1, type=int)
  pagination = query.paginate(page=page, per_page=per_page, error_out=False)

  genres = Genre.query.order_by(Genre.name).all()
  years = get_distinct_years()

  return render_template(
    "main/index.html",
    books=pagination.items,
    pagination=pagination,
    filters=filters,
    genres=genres,
    years=years,
  )
