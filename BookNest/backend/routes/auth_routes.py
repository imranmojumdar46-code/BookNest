"""Register, login, logout."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from controllers import auth_controller

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    form = {}
    if request.method == "POST":
        form = request.form
        errors = auth_controller.register_user(form)
        if not errors:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        for e in errors:
            flash(e, "error")
    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = {}
    if request.method == "POST":
        form = request.form
        user = auth_controller.authenticate(form)
        if user:
            session.clear()                                  # prevents session fixation
            session.update(user_id=user["user_id"], user_name=user["name"])
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("user.dashboard"))
        flash("Invalid email or password.", "error")         # same message for both failures
    return render_template("login.html", form=form)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))
