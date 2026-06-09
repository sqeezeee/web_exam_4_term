from app.extensions import db


class Genre(db.Model):
  """Жанр книги (фантастика, детектив и т.д.)."""

  __tablename__ = "genres"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), nullable=False, unique=True)

  books = db.relationship(
    "Book",
    secondary="book_genre",
    back_populates="genres",
  )

  def __repr__(self):
    return f"<Genre {self.name}>"
