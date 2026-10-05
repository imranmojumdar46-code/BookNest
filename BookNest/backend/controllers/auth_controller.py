"""Registration and login logic."""
from werkzeug.security import check_password_hash, generate_password_hash

import validators
from db import get_db


def register_user(form):
    """Validate and store a new user. Returns a list of error messages (empty = success)."""
    errors, data = validators.validate_registration(form)
    db = get_db()
    if not errors and db.execute("SELECT 1 FROM users WHERE email = ?", (data["email"],)).fetchone():
        errors.append("That email is already registered.")
    if not errors:
        db.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                   (data["name"], data["email"], generate_password_hash(data["password"])))
        db.commit()
    return errors


def authenticate(form):
    """Return the user row if email + password match, otherwise None."""
    email = form.get("email", "").strip().lower()
    user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if user and check_password_hash(user["password"], form.get("password", "")):
        return user
    return None
