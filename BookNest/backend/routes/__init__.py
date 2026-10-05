from .auth_routes import bp as auth_bp
from .book_routes import bp as books_bp
from .main_routes import bp as main_bp
from .user_routes import bp as user_bp


def register_blueprints(app):
    for bp in (main_bp, books_bp, auth_bp, user_bp):
        app.register_blueprint(bp)
