from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
  """Зарегистрированный читатель библиотеки."""

  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True)
  login = db.Column(db.String(64), nullable=False, unique=True)
  password_hash = db.Column(db.String(256), nullable=False)
  last_name = db.Column(db.String(128), nullable=False)
  first_name = db.Column(db.String(128), nullable=False)
  patronymic = db.Column(db.String(128), nullable=True)
  role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

  role = db.relationship("Role", back_populates="users")
  reviews = db.relationship(
    "Review",
    back_populates="user",
    cascade="all, delete-orphan",
    passive_deletes=True,
  )

  def set_password(self, password: str) -> None:
    # pbkdf2 совместим со старыми версиями Python без scrypt в hashlib
    self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

  def check_password(self, password: str) -> bool:
    return check_password_hash(self.password_hash, password)

  @property
  def full_name(self) -> str:
    """ФИО для отображения в навигации."""
    parts = [self.last_name, self.first_name]
    if self.patronymic:
      parts.append(self.patronymic)
    return " ".join(parts)

  def has_role(self, *role_names: str) -> bool:
    return self.role.name in role_names

  def __repr__(self):
    return f"<User {self.login}>"
