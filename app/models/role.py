from app.extensions import db


class Role(db.Model):
  """Роль пользователя в системе (администратор, модератор, пользователь)."""

  __tablename__ = "roles"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), nullable=False, unique=True)
  description = db.Column(db.Text, nullable=False)

  users = db.relationship("User", back_populates="role", lazy="dynamic")

  # Константы для удобной проверки прав в коде
  ADMIN = "administrator"
  MODERATOR = "moderator"
  USER = "user"

  def __repr__(self):
    return f"<Role {self.name}>"
