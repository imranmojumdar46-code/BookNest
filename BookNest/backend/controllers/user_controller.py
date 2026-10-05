"""Profile and account logic."""
from werkzeug.security import check_password_hash, generate_password_hash

import validators
from db import get_db


def get_user(user_id):
    return get_db().execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()


def update_name(user_id, form):
    """Returns (error_or_None, new_name)."""
    name = form.get("name", "").strip()
    if not 2 <= len(name) <= 80:
        return "Name must be 2-80 characters.", None
    db = get_db()
    db.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, user_id))
    db.commit()
    return None, name


def change_password(user, form):
    """Returns an error message, or None when the password was changed."""
    new, confirm = form.get("new_password", ""), form.get("confirm", "")
    if not check_password_hash(user["password"], form.get("current", "")):
        return "Current password is incorrect."
    if validators.password_error(new):
        return validators.password_error(new)
    if new != confirm:
        return "New passwords do not match."
    db = get_db()
    db.execute("UPDATE users SET password = ? WHERE user_id = ?", (generate_password_hash(new), user["user_id"]))
    db.commit()
    return None


def book_count(user_id):
    return get_db().execute("SELECT COUNT(*) FROM books WHERE user_id = ?", (user_id,)).fetchone()[0]
