"""Central settings and constants."""
import os

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
DATABASE_DIR = os.path.join(ROOT_DIR, "database")
SCHEMA_PATH = os.path.join(DATABASE_DIR, "database.sql")
DATABASE_PATH = os.environ.get("BOOKNEST_DB", os.path.join(DATABASE_DIR, "booknest.db"))
UPLOAD_DIR = os.path.join(FRONTEND_DIR, "images", "uploads")

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
MAX_UPLOAD_BYTES = 2 * 1024 * 1024
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

CATEGORIES = ["Fiction", "Non-Fiction", "Science", "Technology", "History",
              "Biography", "Children", "Self-Help", "Other"]
CATEGORY_ICONS = {"Fiction": "📖", "Non-Fiction": "🧠", "Science": "🔬", "Technology": "💻",
                  "History": "🏛️", "Biography": "👤", "Children": "🧸", "Self-Help": "🌱", "Other": "📚"}
# Whitelist: the ORDER BY clause is chosen from here, never taken from user input.
SORTS = {"new": "created_at DESC, book_id DESC", "price_asc": "price ASC",
         "price_desc": "price DESC", "title": "title COLLATE NOCASE ASC"}
