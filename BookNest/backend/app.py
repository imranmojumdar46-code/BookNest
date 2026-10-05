"""BookNest - application entry point.

Run from the project root:   python backend/app.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, abort, render_template, send_from_directory  # noqa: E402

import config  # noqa: E402
import db  # noqa: E402
import security  # noqa: E402
from routes import register_blueprints  # noqa: E402

ERROR_MESSAGES = {400: "Bad request.", 403: "You are not allowed to do that.",
                  404: "Page not found.", 413: "That file is too large (max 2 MB)."}


def create_app():
    # HTML pages live in ../frontend ; CSS/JS/images are served through /assets/...
    app = Flask(__name__, template_folder=config.FRONTEND_DIR, static_folder=None)
    app.config.update(SECRET_KEY=config.SECRET_KEY, MAX_CONTENT_LENGTH=config.MAX_UPLOAD_BYTES,
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
    app.teardown_appcontext(db.close_db)
    app.before_request(security.csrf_protect)
    app.context_processor(security.template_globals)
    register_blueprints(app)

    @app.route("/assets/<folder>/<path:filename>")
    def assets(folder, filename):
        if folder not in ("css", "js", "images"):      # never expose the .html templates
            abort(404)
        resp = send_from_directory(os.path.join(config.FRONTEND_DIR, folder), filename, max_age=0)
        resp.headers["Cache-Control"] = "no-cache"          # always re-check, so edits show up at once
        return resp

    @app.errorhandler(400)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(413)
    def http_error(err):
        return render_template("error.html", code=err.code, message=ERROR_MESSAGES.get(err.code, "Error")), err.code

    db.init_db()
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
