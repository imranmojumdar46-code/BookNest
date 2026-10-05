"""Server-side validation. Each function returns (errors, cleaned_data)."""
import re

import config

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def password_error(pw):
    if len(pw) < 8 or not re.search(r"[A-Za-z]", pw) or not re.search(r"\d", pw):
        return "Password must be at least 8 characters and include a letter and a number."


def validate_registration(form):
    name = form.get("name", "").strip()
    email = form.get("email", "").strip().lower()
    pw, confirm = form.get("password", ""), form.get("confirm", "")
    errors = []
    if not 2 <= len(name) <= 80:
        errors.append("Name must be 2-80 characters.")
    if not EMAIL_RE.match(email):
        errors.append("Enter a valid email address.")
    if password_error(pw):
        errors.append(password_error(pw))
    if pw != confirm:
        errors.append("Passwords do not match.")
    return errors, {"name": name, "email": email, "password": pw}


def validate_contact(form):
    name = form.get("name", "").strip()
    email = form.get("email", "").strip()
    message = form.get("message", "").strip()
    errors = []
    if not 2 <= len(name) <= 80:
        errors.append("Name must be 2-80 characters.")
    if not EMAIL_RE.match(email):
        errors.append("Enter a valid email address.")
    if not 10 <= len(message) <= 1000:
        errors.append("Message must be 10-1000 characters.")
    return errors, {"name": name, "email": email, "message": message}


def validate_book(form):
    data = {k: form.get(k, "").strip() for k in ("title", "author", "category", "description")}
    errors, price = [], None
    if not 1 <= len(data["title"]) <= 150:
        errors.append("Title is required (max 150 characters).")
    if not 1 <= len(data["author"]) <= 100:
        errors.append("Author is required (max 100 characters).")
    if data["category"] not in config.CATEGORIES:
        errors.append("Please choose a valid category.")
    try:
        price = round(float(form.get("price", "")), 2)
        if not 0 <= price <= 100000:
            raise ValueError
    except ValueError:
        errors.append("Price must be a number between 0 and 100000.")
    if len(data["description"]) > 1000:
        errors.append("Description must be 1000 characters or fewer.")
    data["price"] = price
    return errors, data
