"""Books: catalogue, detail page, add / edit / delete (CRUD) and wishlist toggle."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from controllers import book_controller as books
from security import login_required

bp = Blueprint("books", __name__)


@bp.route("/books")
def catalog():
    q = request.args.get("q", "").strip()
    cat = request.args.get("category", "").strip()
    sort = request.args.get("sort", "new")
    return render_template("books.html", books=books.search_books(q, cat, sort), q=q, cat=cat, sort=sort)


@bp.route("/books/<int:book_id>")
def detail(book_id):
    book = books.get_book(book_id)
    uid = session.get("user_id")
    return render_template("book_detail.html", book=book, related=books.related_books(book),
                           is_owner=uid == book["user_id"],
                           fav=bool(uid) and books.is_favorite(uid, book_id))


@bp.route("/books/add", methods=["GET", "POST"])
@login_required
def add():
    form = {}
    if request.method == "POST":
        form = request.form
        errors = books.create_book(session["user_id"], form, request.files.get("image"))
        if not errors:
            flash("Book added successfully.", "success")
            return redirect(url_for("user.dashboard"))
        for e in errors:
            flash(e, "error")
    return render_template("book_form.html", book=None, form=form, mode="Add")


@bp.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
@login_required
def edit(book_id):
    book = books.get_owned_book(book_id, session["user_id"])
    form = {}
    if request.method == "POST":
        form = request.form
        errors = books.update_book(book, form, request.files.get("image"))
        if not errors:
            flash("Book updated.", "success")
            return redirect(url_for("user.dashboard"))
        for e in errors:
            flash(e, "error")
    return render_template("book_form.html", book=dict(book), form=form, mode="Edit")


@bp.route("/books/<int:book_id>/delete", methods=["POST"])
@login_required
def delete(book_id):
    books.delete_book(books.get_owned_book(book_id, session["user_id"]))
    flash("Book deleted.", "success")
    return redirect(url_for("user.dashboard"))


@bp.route("/books/<int:book_id>/favorite", methods=["POST"])
@login_required
def favorite(book_id):
    now_fav = books.toggle_favorite(session["user_id"], book_id)
    flash("Added to your wishlist ♥" if now_fav else "Removed from your wishlist.", "success")
    nxt = request.form.get("next", "")
    if not nxt.startswith("/") or nxt.startswith("//") or "\\" in nxt:   # same-site redirects only
        nxt = url_for("books.detail", book_id=book_id)
    return redirect(nxt)
