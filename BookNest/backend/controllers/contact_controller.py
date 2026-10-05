"""Contact / feedback messages."""
import validators
from db import get_db


def save_message(form):
    """Validate and store a message. Returns a list of errors (empty = saved)."""
    errors, data = validators.validate_contact(form)
    if not errors:
        db = get_db()
        db.execute("INSERT INTO messages (user_name, email, message) VALUES (?, ?, ?)",
                   (data["name"], data["email"], data["message"]))
        db.commit()
    return errors
