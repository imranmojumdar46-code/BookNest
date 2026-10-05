"""Logged-in area: dashboard, profile, wishlist."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from controllers import book_controller, user_controller
from security import login_required

bp = Blueprint("user", __name__)


@bp.route("/dashboard")
@login_required
def dashboard():
    user = user_controller.get_user(session["user_id"])
    mine = book_controller.user_books(user["user_id"])
    return render_template("dashboard.html", user=user, books=mine, total=sum(b["price"] for b in mine))


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = user_controller.get_user(session["user_id"])
    if request.method == "POST":
        if request.form.get("action") == "name":
            error, name = user_controller.update_name(user["user_id"], request.form)
            if error:
                flash(error, "error")
            else:
                session["user_name"] = name
                flash("Name updated.", "success")
        elif request.form.get("action") == "password":
            error = user_controller.change_password(user, request.form)
            flash(error or "Password changed.", "error" if error else "success")
        return redirect(url_for("user.profile"))
    return render_template("profile.html", user=user, count=user_controller.book_count(user["user_id"]))


@bp.route("/wishlist")
@login_required
def wishlist():
    return render_template("wishlist.html", books=book_controller.wishlist(session["user_id"]))
