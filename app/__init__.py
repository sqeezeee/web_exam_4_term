from pathlib import Path

from flask import Flask

from app.config import Config
from app.extensions import db, login_manager

from sqlalchemy import event
from sqlalchemy.engine import Engine

# Корень проекта — на уровень выше пакета app
BASE_DIR = Path(__file__).resolve().parent.parent


def create_app(config_class=Config):
  app = Flask(
    __name__,
    instance_relative_config=True,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
  )
  app.config.from_object(config_class)

  # Создаём папку для загрузок, если её ещё нет
  app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)

  db.init_app(app)
  # Принудительно включаем каскадное удаление для SQLite
  if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
      @event.listens_for(Engine, "connect")
      def set_sqlite_pragma(dbapi_connection, connection_record):
          cursor = dbapi_connection.cursor()
          cursor.execute("PRAGMA foreign_keys=ON")
          cursor.close()
  login_manager.init_app(app)

  from app.models import User

  @login_manager.user_loader
  def load_user(user_id):
    return db.session.get(User, int(user_id))

  from app.blueprints.auth import auth_bp
  from app.blueprints.books import books_bp
  from app.blueprints.main import main_bp
  from app.blueprints.reviews import reviews_bp

  app.register_blueprint(main_bp)
  app.register_blueprint(auth_bp)
  app.register_blueprint(books_bp)
  app.register_blueprint(reviews_bp)

  return app
