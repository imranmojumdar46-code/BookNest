"""Public pages: home, about, FAQ, categories, contact."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from controllers import book_controller, contact_controller

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    latest, stats = book_controller.home_data()
    return render_template("index.html", latest=latest, stats=stats)


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/faq")
def faq():
    return render_template("faq.html")


@bp.route("/categories")
def categories():
    return render_template("categories.html", counts=book_controller.category_counts())


@bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = {}
    if request.method == "POST":
        form = request.form
        errors = contact_controller.save_message(form)
        if not errors:
            flash("Thank you! Your message has been received.", "success")
            return redirect(url_for("main.contact"))
        for e in errors:
            flash(e, "error")
    return render_template("contact.html", form=form)
