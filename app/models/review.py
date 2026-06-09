from datetime import datetime, timezone

from app.extensions import db


class Review(db.Model):
  """Рецензия читателя на книгу."""

  __tablename__ = "reviews"

  id = db.Column(db.Integer, primary_key=True)
  book_id = db.Column(
    db.Integer,
    db.ForeignKey("books.id", ondelete="CASCADE"),
    nullable=False,
  )
  user_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False,
  )
  rating = db.Column(db.Integer, nullable=False)
  text = db.Column(db.Text, nullable=False)
  created_at = db.Column(
    db.DateTime,
    nullable=False,
    default=lambda: datetime.now(timezone.utc),
  )

  book = db.relationship("Book", back_populates="reviews")
  user = db.relationship("User", back_populates="reviews")

  # Один пользователь может оставить только одну рецензию на книгу
  __table_args__ = (
    db.UniqueConstraint("book_id", "user_id", name="uq_review_book_user"),
  )

  # Подписи для селектора оценки в форме
  RATING_CHOICES = [
    (5, "отлично"),
    (4, "хорошо"),
    (3, "удовлетворительно"),
    (2, "неудовлетворительно"),
    (1, "плохо"),
    (0, "ужасно"),
  ]

  @property
  def rating_label(self) -> str:
    for value, label in self.RATING_CHOICES:
      if value == self.rating:
        return label
    return str(self.rating)

  def __repr__(self):
    return f"<Review book={self.book_id} user={self.user_id}>"
