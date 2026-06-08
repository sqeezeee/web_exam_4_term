from pathlib import Path

from flask import (
  Blueprint,
  current_app,
  flash,
  redirect,
  render_template,
  request,
  url_for,
)
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from app.decorators import role_required
from app.extensions import db
from app.models.book import Book
from app.models.genre import Genre
from app.models.role import Role
from app.services.cover_service import delete_cover_file, save_cover
from app.services.markdown_service import render_markdown, sanitize_markdown

books_bp = Blueprint("books", __name__, url_prefix="/books")


def _parse_book_form(form, require_cover: bool = False):
  """Читаем и валидируем поля формы книги."""
  title = form.get("title", "").strip()
  description_raw = form.get("description", "")
  year = form.get("year", type=int)
  publisher = form.get("publisher", "").strip()
  author = form.get("author", "").strip()
  pages = form.get("pages", type=int)
  genre_ids = [int(g) for g in form.getlist("genre_ids") if g.isdigit()]

  errors = []
  if not title:
    errors.append("title")
  if not description_raw.strip():
    errors.append("description")
  if not year:
    errors.append("year")
  if not publisher:
    errors.append("publisher")
  if not author:
    errors.append("author")
  if not pages:
    errors.append("pages")
  if not genre_ids:
    errors.append("genre_ids")

  cover_file = request.files.get("cover")
  if require_cover and (not cover_file or not cover_file.filename):
    errors.append("cover")

  return {
    "title": title,
    "description": sanitize_markdown(description_raw),
    "year": year,
    "publisher": publisher,
    "author": author,
    "pages": pages,
    "genre_ids": genre_ids,
    "cover_file": cover_file,
    "errors": errors,
  }


@books_bp.route("/<int:book_id>")
def detail(book_id):
  """Страница просмотра книги — доступна всем, в том числе гостям."""
  book = Book.query.get_or_404(book_id)
  description_html = render_markdown(book.description)

  user_review = None
  can_review = False
  if current_user.is_authenticated:
    user_review = next((r for r in book.reviews if r.user_id == current_user.id), None)
    can_review = user_review is None

  reviews_html = [
    (review, render_markdown(review.text))
    for review in sorted(book.reviews, key=lambda r: r.created_at, reverse=True)
  ]

  user_review_html = render_markdown(user_review.text) if user_review else None

  return render_template(
    "books/detail.html",
    book=book,
    description_html=description_html,
    reviews_html=reviews_html,
    user_review=user_review,
    user_review_html=user_review_html,
    can_review=can_review,
  )


@books_bp.route("/create", methods=["GET", "POST"])
@login_required
@role_required(Role.ADMIN)
def create():
  genres = Genre.query.order_by(Genre.name).all()
  form_data = {}

  if request.method == "POST":
    parsed = _parse_book_form(request.form, require_cover=True)
    form_data = parsed

    if parsed["errors"]:
      flash(
        "При сохранении данных возникла ошибка. Проверьте корректность введённых данных.",
        "danger",
      )
      return render_template(
        "books/create.html",
        genres=genres,
        form_data=form_data,
      )

    try:
      book = Book(
        title=parsed["title"],
        description=parsed["description"],
        year=parsed["year"],
        publisher=parsed["publisher"],
        author=parsed["author"],
        pages=parsed["pages"],
      )
      book.genres = Genre.query.filter(Genre.id.in_(parsed["genre_ids"])).all()
      db.session.add(book)
      db.session.flush()

      upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
      save_cover(parsed["cover_file"], book.id, upload_folder)

      db.session.commit()
      flash("Книга успешно добавлена", "success")
      return redirect(url_for("books.detail", book_id=book.id))

    except SQLAlchemyError:
      db.session.rollback()
      flash(
        "При сохранении данных возникла ошибка. Проверьте корректность введённых данных.",
        "danger",
      )

  return render_template("books/create.html", genres=genres, form_data=form_data)


@books_bp.route("/<int:book_id>/edit", methods=["GET", "POST"])
@login_required
@role_required(Role.ADMIN, Role.MODERATOR)
def edit(book_id):
  book = Book.query.get_or_404(book_id)
  genres = Genre.query.order_by(Genre.name).all()

  form_data = {
    "title": book.title,
    "description": book.description,
    "year": book.year,
    "publisher": book.publisher,
    "author": book.author,
    "pages": book.pages,
    "genre_ids": [g.id for g in book.genres],
  }

  if request.method == "POST":
    parsed = _parse_book_form(request.form, require_cover=False)
    form_data = parsed

    if parsed["errors"]:
      flash(
        "При сохранении данных возникла ошибка. Проверьте корректность введённых данных.",
        "danger",
      )
      return render_template(
        "books/edit.html",
        book=book,
        genres=genres,
        form_data=form_data,
      )

    try:
      book.title = parsed["title"]
      book.description = parsed["description"]
      book.year = parsed["year"]
      book.publisher = parsed["publisher"]
      book.author = parsed["author"]
      book.pages = parsed["pages"]
      book.genres = Genre.query.filter(Genre.id.in_(parsed["genre_ids"])).all()

      db.session.commit()
      flash("Данные книги обновлены", "success")
      return redirect(url_for("books.detail", book_id=book.id))

    except SQLAlchemyError:
      db.session.rollback()
      flash(
        "При сохранении данных возникла ошибка. Проверьте корректность введённых данных.",
        "danger",
      )

  return render_template(
    "books/edit.html",
    book=book,
    genres=genres,
    form_data=form_data,
  )


@books_bp.route("/<int:book_id>/delete", methods=["POST"])
@login_required
@role_required(Role.ADMIN)
def delete(book_id):
  book = Book.query.get_or_404(book_id)
  upload_folder = Path(current_app.config["UPLOAD_FOLDER"])

  cover = book.cover
  title = book.title

  try:
    if cover:
      delete_cover_file(cover, upload_folder)

    db.session.delete(book)
    db.session.commit()
    flash(f'Книга «{title}» успешно удалена', "success")

  except SQLAlchemyError:
    db.session.rollback()
    flash("При удалении книги возникла ошибка", "danger")

  return redirect(url_for("main.index"))
