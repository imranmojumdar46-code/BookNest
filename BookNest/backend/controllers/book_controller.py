"""Book CRUD, search, wishlist and image handling."""
import os
import uuid

from flask import abort

import config
import validators
from db import get_db


# ---------- READ ----------
def home_data():
    db = get_db()
    latest = db.execute("SELECT * FROM books ORDER BY created_at DESC, book_id DESC LIMIT 4").fetchall()
    stats = db.execute("SELECT (SELECT COUNT(*) FROM books) b, (SELECT COUNT(*) FROM users) u, "
                       "(SELECT COUNT(DISTINCT category) FROM books) c").fetchone()
    return latest, stats


def category_counts():
    rows = get_db().execute("SELECT category, COUNT(*) n FROM books GROUP BY category").fetchall()
    return {r["category"]: r["n"] for r in rows}


def search_books(q, category, sort):
    sql, params = "SELECT * FROM books WHERE 1=1", []
    if q:
        sql += " AND (title LIKE ? OR author LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]
    if category in config.CATEGORIES:
        sql += " AND category = ?"
        params.append(category)
    order = config.SORTS.get(sort, config.SORTS["new"])
    return get_db().execute(f"{sql} ORDER BY {order}", params).fetchall()


def get_book(book_id):
    book = get_db().execute("SELECT b.*, u.name AS owner FROM books b JOIN users u ON u.user_id = b.user_id "
                            "WHERE b.book_id = ?", (book_id,)).fetchone()
    if book is None:
        abort(404)
    return book


def related_books(book):
    return get_db().execute("SELECT * FROM books WHERE category = ? AND book_id != ? "
                            "ORDER BY book_id DESC LIMIT 4", (book["category"], book["book_id"])).fetchall()


def user_books(user_id):
    return get_db().execute("SELECT * FROM books WHERE user_id = ? ORDER BY created_at DESC, book_id DESC",
                            (user_id,)).fetchall()


def get_owned_book(book_id, user_id):
    book = get_db().execute("SELECT * FROM books WHERE book_id = ?", (book_id,)).fetchone()
    if book is None:
        abort(404)
    if book["user_id"] != user_id:
        abort(403)
    return book


# ---------- IMAGES ----------
def save_image(file):
    """Returns (stored_filename_or_None, error_or_None). Uploading is optional."""
    if not file or not file.filename:
        return None, None
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in config.ALLOWED_EXT:
        return None, "Image must be PNG, JPG, GIF or WEBP."
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    name = f"{uuid.uuid4().hex}.{ext}"           # random name: no path tricks, no collisions
    file.save(os.path.join(config.UPLOAD_DIR, name))
    return name, None


def remove_image(name):
    if name:
        path = os.path.join(config.UPLOAD_DIR, os.path.basename(name))
        if os.path.isfile(path):
            os.remove(path)


# ---------- CREATE / UPDATE / DELETE ----------
def create_book(user_id, form, file):
    errors, data = validators.validate_book(form)
    image, img_err = save_image(file)
    if img_err:
        errors.append(img_err)
    if errors:
        remove_image(image)
        return errors
    db = get_db()
    db.execute("INSERT INTO books (user_id, title, author, category, price, description, image) "
               "VALUES (?,?,?,?,?,?,?)",
               (user_id, data["title"], data["author"], data["category"], data["price"],
                data["description"], image))
    db.commit()
    return []


def update_book(book, form, file):
    errors, data = validators.validate_book(form)
    image, img_err = save_image(file)
    if img_err:
        errors.append(img_err)
    if errors:
        remove_image(image)
        return errors
    db = get_db()
    db.execute("UPDATE books SET title=?, author=?, category=?, price=?, description=?, image=? WHERE book_id=?",
               (data["title"], data["author"], data["category"], data["price"], data["description"],
                image or book["image"], book["book_id"]))
    db.commit()
    if image:
        remove_image(book["image"])
    return []


def delete_book(book):
    db = get_db()
    db.execute("DELETE FROM books WHERE book_id = ?", (book["book_id"],))
    db.commit()
    remove_image(book["image"])


# ---------- WISHLIST ----------
def is_favorite(user_id, book_id):
    return get_db().execute("SELECT 1 FROM favorites WHERE user_id = ? AND book_id = ?",
                            (user_id, book_id)).fetchone() is not None


def toggle_favorite(user_id, book_id):
    """Add or remove a favourite. Returns True if it is now a favourite."""
    get_book(book_id)                            # 404 if the book does not exist
    db = get_db()
    now_fav = not is_favorite(user_id, book_id)
    if now_fav:
        db.execute("INSERT INTO favorites (user_id, book_id) VALUES (?, ?)", (user_id, book_id))
    else:
        db.execute("DELETE FROM favorites WHERE user_id = ? AND book_id = ?", (user_id, book_id))
    db.commit()
    return now_fav


def wishlist(user_id):
    return get_db().execute("SELECT b.* FROM books b JOIN favorites f ON f.book_id = b.book_id "
                            "WHERE f.user_id = ? ORDER BY f.created_at DESC", (user_id,)).fetchall()
