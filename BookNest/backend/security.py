"""CSRF protection, login guard and template globals."""
import secrets
from functools import wraps

from flask import abort, flash, redirect, request, session, url_for

import config


def csrf_protect():
    """Reject every POST that does not carry the session's CSRF token."""
    if request.method == "POST":
        token = session.get("csrf_token")
        if not token or token != request.form.get("csrf_token"):
            abort(400)


def template_globals():
    def csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(16)
        return session["csrf_token"]
    return {"csrf_token": csrf_token, "categories": config.CATEGORIES,
            "cat_icons": config.CATEGORY_ICONS, "current_user": session.get("user_name")}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped
