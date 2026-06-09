from sqlalchemy import func

from app.extensions import db

# Связующая таблица «книга — жанр» (многие ко многим)
book_genre = db.Table(
  "book_genre",
  db.Column(
    "book_id",
    db.Integer,
    db.ForeignKey("books.id", ondelete="CASCADE"),
    primary_key=True,
  ),
  db.Column(
    "genre_id",
    db.Integer,
    db.ForeignKey("genres.id", ondelete="CASCADE"),
    primary_key=True,
  ),
)


class Book(db.Model):
  """Книга в электронном каталоге."""

  __tablename__ = "books"

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(256), nullable=False)
  description = db.Column(db.Text, nullable=False)
  year = db.Column(db.Integer, nullable=False)
  publisher = db.Column(db.String(256), nullable=False)
  author = db.Column(db.String(256), nullable=False)
  pages = db.Column(db.Integer, nullable=False)

  genres = db.relationship(
    "Genre",
    secondary=book_genre,
    back_populates="books",
  )
  cover = db.relationship(
    "Cover",
    back_populates="book",
    uselist=False,
    cascade="all, delete-orphan",
    passive_deletes=True,
  )
  reviews = db.relationship(
    "Review",
    back_populates="book",
    cascade="all, delete-orphan",
    passive_deletes=True,
  )

  @property
  def average_rating(self):
    """Средняя оценка по всем рецензиям (None, если рецензий нет)."""
    from app.models.review import Review

    result = (
      db.session.query(func.avg(Review.rating))
      .filter(Review.book_id == self.id)
      .scalar()
    )
    return round(float(result), 1) if result is not None else None

  @property
  def reviews_count(self) -> int:
    return len(self.reviews)

  def __repr__(self):
    return f"<Book {self.title}>"
