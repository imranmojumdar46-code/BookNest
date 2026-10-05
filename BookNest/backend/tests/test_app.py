"""Run from the project root:  python -m unittest discover backend/tests -v"""
import os
import sqlite3
import sys
import tempfile
import unittest

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["BOOKNEST_DB"] = _tmp.name
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402
from app import app  # noqa: E402

BOOK = dict(title="Test Book", author="Tester", category="Fiction", price="9.99", description="x")


def query(sql):
    return sqlite3.connect(os.environ["BOOKNEST_DB"]).execute(sql).fetchall()


class BookNestTests(unittest.TestCase):
    def setUp(self):
        self.c = app.test_client()

    def token(self):
        self.c.get("/login")
        with self.c.session_transaction() as s:
            return s["csrf_token"]

    def post(self, url, data, **kw):
        return self.c.post(url, data={**data, "csrf_token": self.token()}, **kw)

    def register(self, email="a@test.com", pw="Passw0rd1", name="Alice"):
        return self.post("/register", dict(name=name, email=email, password=pw, confirm=pw), follow_redirects=True)

    def login(self, email="a@test.com", pw="Passw0rd1"):
        return self.post("/login", dict(email=email, password=pw), follow_redirects=True)

    # ---------- pages / frontend ----------
    def test_public_pages(self):
        for url in ("/", "/about", "/books", "/contact", "/login", "/register", "/faq", "/categories",
                    "/books/1", "/books?sort=price_asc", "/books?sort=bogus"):
            self.assertEqual(self.c.get(url).status_code, 200, url)

    def test_assets_served_and_templates_hidden(self):
        for url in ("/assets/css/style.css", "/assets/js/script.js", "/assets/images/hero.svg",
                    "/assets/images/logo.svg", "/assets/images/about.svg", "/assets/images/contact.svg"):
            with self.c.get(url) as r:
                self.assertEqual(r.status_code, 200, url)
        for url in ("/assets/templates/base.html", "/assets/frontend/base.html", "/assets/css/../base.html"):
            with self.c.get(url) as r:
                self.assertEqual(r.status_code, 404, url)

    def test_semantic_html_no_inline_css(self):
        html = self.c.get("/").data.decode()
        for tag in ("<header", "<nav", "<main", "<section", "<article", "<footer", "<figure"):
            self.assertIn(tag, html)
        self.assertNotIn(' style="', html)
        self.assertIn('id="themeToggle"', html)

    # ---------- registration / login ----------
    def test_csrf_required(self):
        self.assertEqual(self.c.post("/login", data={"email": "x"}).status_code, 400)

    def test_register_validation_and_hashing(self):
        self.assertIn(b"at least 8", self.register("bad@test.com", "short").data)
        self.assertIn(b"Registration successful", self.register().data)
        self.assertIn(b"already registered", self.register().data)
        stored = query("SELECT password FROM users WHERE email='a@test.com'")[0][0]
        self.assertNotEqual(stored, "Passw0rd1")

    def test_login_logout_and_protection(self):
        self.assertEqual(self.c.get("/dashboard").status_code, 302)
        self.register("b@test.com")
        self.assertIn(b"Invalid email or password", self.login("b@test.com", "wrong1234").data)
        self.assertIn(b"Welcome back", self.login("b@test.com").data)
        self.assertEqual(self.c.get("/dashboard").status_code, 200)
        self.post("/logout", {})
        self.assertEqual(self.c.get("/dashboard").status_code, 302)

    # ---------- CRUD ----------
    def test_book_crud_and_ownership(self):
        self.register("owner@test.com"); self.login("owner@test.com")
        self.assertIn(b"Book added", self.post("/books/add", BOOK, follow_redirects=True).data)
        self.assertIn(b"Price must be", self.post("/books/add", {**BOOK, "price": "-5"}, follow_redirects=True).data)
        bid = query("SELECT book_id FROM books WHERE title='Test Book'")[0][0]
        self.assertIn(b"Book updated", self.post(f"/books/{bid}/edit", {**BOOK, "title": "Renamed"}, follow_redirects=True).data)
        self.post("/logout", {})
        self.register("other@test.com"); self.login("other@test.com")
        self.assertEqual(self.c.get(f"/books/{bid}/edit").status_code, 403)
        self.assertEqual(self.post(f"/books/{bid}/delete", {}).status_code, 403)
        self.post("/logout", {}); self.login("owner@test.com")
        self.assertIn(b"Book deleted", self.post(f"/books/{bid}/delete", {}, follow_redirects=True).data)
        self.assertEqual(query(f"SELECT COUNT(*) FROM books WHERE book_id={bid}")[0][0], 0)

    def test_image_upload_and_cleanup(self):
        import io
        self.register("u@test.com"); self.login("u@test.com")
        png = b"\x89PNG\r\n\x1a\n" + b"0" * 20
        self.post("/books/add", {**BOOK, "title": "With Cover", "image": (io.BytesIO(png), "c.png")},
                  content_type="multipart/form-data", follow_redirects=True)
        name, bid = query("SELECT image, book_id FROM books WHERE title='With Cover'")[0]
        self.assertTrue(os.path.isfile(os.path.join(config.UPLOAD_DIR, name)))
        with self.c.get(f"/assets/images/uploads/{name}") as r:
            self.assertEqual(r.status_code, 200)
        bad = self.post("/books/add", {**BOOK, "title": "Bad", "image": (io.BytesIO(b"x"), "evil.exe")},
                        content_type="multipart/form-data", follow_redirects=True)
        self.assertIn(b"Image must be", bad.data)
        self.post(f"/books/{bid}/delete", {}, follow_redirects=True)
        self.assertFalse(os.path.isfile(os.path.join(config.UPLOAD_DIR, name)))

    def test_search_filter(self):
        self.assertIn(b"Zen: The Art of Simple Living", self.c.get("/books?q=masuno").data)
        self.assertNotIn(b"Zen: The Art of Simple Living", self.c.get("/books?category=Science").data)

    # ---------- contact ----------
    def test_contact_validation_and_storage(self):
        bad = self.post("/contact", dict(name="Al", email="a@b.co", message="hi"), follow_redirects=True)
        self.assertIn(b"Message must be", bad.data)
        ok = self.post("/contact", dict(name="Al", email="a@b.co", message="Hello there team!"), follow_redirects=True)
        self.assertIn(b"received", ok.data)
        row = query("SELECT user_name, email, message FROM messages WHERE email='a@b.co'")
        self.assertEqual(row, [("Al", "a@b.co", "Hello there team!")])

    # ---------- profile / wishlist ----------
    def test_detail_404_and_profile_protection(self):
        self.assertEqual(self.c.get("/books/99999").status_code, 404)
        self.assertEqual(self.c.get("/profile").status_code, 302)
        self.assertIn(b"Zen: The Art of Simple Living", self.c.get("/books/4").data)

    def test_profile_update(self):
        self.register("p@test.com"); self.login("p@test.com")
        self.assertIn(b"Name updated", self.post("/profile", dict(action="name", name="Pat"), follow_redirects=True).data)
        self.assertIn(b"Current password is incorrect", self.post("/profile", dict(
            action="password", current="nope", new_password="NewPass123", confirm="NewPass123"), follow_redirects=True).data)
        self.assertIn(b"Password changed", self.post("/profile", dict(
            action="password", current="Passw0rd1", new_password="NewPass123", confirm="NewPass123"), follow_redirects=True).data)
        self.post("/logout", {})
        self.assertIn(b"Welcome back", self.login("p@test.com", "NewPass123").data)

    def test_wishlist(self):
        self.assertEqual(self.c.get("/wishlist").status_code, 302)
        self.register("w@test.com"); self.login("w@test.com")
        self.assertIn(b"Added to your wishlist", self.post("/books/2/favorite", {}, follow_redirects=True).data)
        self.assertIn(b"Biology Second Paper", self.c.get("/wishlist").data)
        self.assertIn(b"Removed from your wishlist",
                      self.post("/books/2/favorite", {"next": "//evil.com"}, follow_redirects=True).data)


if __name__ == "__main__":
    unittest.main()
