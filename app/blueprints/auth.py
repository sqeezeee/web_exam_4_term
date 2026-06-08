from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
  if current_user.is_authenticated:
    return redirect(url_for("main.index"))

  if request.method == "POST":
    login_val = request.form.get("login", "").strip()
    password = request.form.get("password", "")
    remember = request.form.get("remember") == "on"

    user = User.query.filter_by(login=login_val).first()
    if user and user.check_password(password):
      login_user(user, remember=remember)
      next_page = request.args.get("next")
      if next_page:
        return redirect(next_page)
      return redirect(url_for("main.index"))

    flash("Невозможно аутентифицироваться с указанными логином и паролем", "danger")

  return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
  logout_user()
  # Возвращаем на ту страницу, с которой вышли, или на главную
  next_page = request.args.get("next") or request.referrer
  if next_page and url_for("auth.login") not in next_page:
    return redirect(next_page)
  return redirect(url_for("main.index"))
