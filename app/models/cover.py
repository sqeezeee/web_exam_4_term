from app.extensions import db


class Cover(db.Model):
  """Метаданные файла обложки книги."""

  __tablename__ = "covers"

  id = db.Column(db.Integer, primary_key=True)
  filename = db.Column(db.String(256), nullable=False)
  mime_type = db.Column(db.String(128), nullable=False)
  # Хэш для дедупликации файлов (не unique — одно изображение может быть у разных книг)
  md5_hash = db.Column(db.String(32), nullable=False)
  book_id = db.Column(
    db.Integer,
    db.ForeignKey("books.id", ondelete="CASCADE"),
    nullable=False,
    unique=True,
  )

  book = db.relationship("Book", back_populates="cover")

  def __repr__(self):
    return f"<Cover {self.filename}>"
