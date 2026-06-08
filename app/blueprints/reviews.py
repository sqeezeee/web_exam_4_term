from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.book import Book
from app.models.review import Review
from app.services.markdown_service import sanitize_markdown

reviews_bp = Blueprint("reviews", __name__, url_prefix="/reviews")


@reviews_bp.route("/create/<int:book_id>", methods=["GET", "POST"])
@login_required
def create(book_id):
  """Создание рецензии — доступно любому аутентифицированному пользователю."""
  book = Book.query.get_or_404(book_id)

  existing = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()
  if existing:
    return redirect(url_for("books.detail", book_id=book_id))

  form_data = {"rating": 5, "text": ""}

  if request.method == "POST":
    rating = request.form.get("rating", type=int)
    text_raw = request.form.get("text", "")
    form_data = {"rating": rating, "text": text_raw}

    valid_ratings = [choice[0] for choice in Review.RATING_CHOICES]
    if rating not in valid_ratings or not text_raw.strip():
      flash(
        "При сохранении данных возникла ошибка. Проверьте корректность введённых данных.",
        "danger",
      )
      return render_template(
        "reviews/create.html",
        book=book,
        form_data=form_data,
        rating_choices=Review.RATING_CHOICES,
      )

    try:
      review = Review(
        book_id=book_id,
        user_id=current_user.id,
        rating=rating,
        text=sanitize_markdown(text_raw),
      )
      db.session.add(review)
      db.session.commit()
      flash("Рецензия успешно добавлена", "success")
      return redirect(url_for("books.detail", book_id=book_id))

    except SQLAlchemyError:
      db.session.rollback()
      flash(
        "При сохранении данных возникла ошибка. Проверьте корректность введённых данных.",
        "danger",
      )

  return render_template(
    "reviews/create.html",
    book=book,
    form_data=form_data,
    rating_choices=Review.RATING_CHOICES,
  )
