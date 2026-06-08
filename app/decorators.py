from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def role_required(*role_names):
  """
  Декоратор: доступ только для указанных ролей.
  Неаутентифицированных перенаправляет на вход (через login_required выше по цепочке).
  """
  def decorator(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
      if not current_user.is_authenticated:
        flash(
          "Для выполнения данного действия необходимо пройти процедуру аутентификации",
          "warning",
        )
        return redirect(url_for("auth.login"))

      if not current_user.has_role(*role_names):
        flash("У вас недостаточно прав для выполнения данного действия", "danger")
        return redirect(url_for("main.index"))

      return view_func(*args, **kwargs)

    return wrapped

  return decorator
