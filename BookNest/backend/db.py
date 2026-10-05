"""SQLite connection helpers and first-run set-up."""
import os
import sqlite3

from flask import g
from werkzeug.security import generate_password_hash

import config


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(config.DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


# (title, author, category, price, description, cover file in frontend/images/uploads/)
SAMPLE_BOOKS = [
    ("To the Bright Edge of the World", "Eowyn Ivey", "Fiction", 15.99,
     "An epic tale of love, survival and wonder set in the Alaskan wilderness.",
     "to-the-bright-edge-of-the-world.jpg"),
    ("Biology Second Paper (Classes XI-XII)", "Gazi Azmal & Gazi Asmat", "Science", 8.50,
     "Written in accordance with the latest NCTB syllabus. Published by Gazi Publishers.",
     "biology-second-paper.jpg"),
    ("IT Project Management: On Track from Start to Finish (3rd Edition)", "Joseph Phillips", "Technology", 34.00,
     "Lead IT projects and manage cost, schedule, scope, quality and risk. Prepares you for the CompTIA Project+ exam.",
     "it-project-management.jpg"),
    ("Zen: The Art of Simple Living", "Shunmyō Masuno", "Self-Help", 12.75,
     "Practical Zen teachings for a calmer, simpler everyday life, from a bestselling Japanese author.",
     "zen-the-art-of-simple-living.jpg"),
]


OLD_SAMPLE_TITLES = ("The Midnight Library", "Atomic Habits", "A Brief History of Time",
                     "Clean Code", "Sapiens", "The Diary of a Young Girl")


def init_db():
    """Create the tables from database/database.sql; add / refresh demo data."""
    os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    with open(config.SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
    row = conn.execute("SELECT user_id FROM users WHERE email = 'demo@booknest.com'").fetchone()
    if row is None and conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        cur = conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                           ("Demo User", "demo@booknest.com", generate_password_hash("Demo@1234")))
        row = (cur.lastrowid,)
    if row is not None:
        demo_id = row[0]
        # upgrade older databases: drop the old text-only sample books of the demo account
        conn.executemany("DELETE FROM books WHERE user_id = ? AND title = ? AND image IS NULL",
                         [(demo_id, t) for t in OLD_SAMPLE_TITLES])
        # add the sample books that are missing (matched by title, so nothing is duplicated)
        for b in SAMPLE_BOOKS:
            if conn.execute("SELECT 1 FROM books WHERE title = ?", (b[0],)).fetchone() is None:
                conn.execute("INSERT INTO books (user_id, title, author, category, price, description, image) "
                             "VALUES (?,?,?,?,?,?,?)", (demo_id, *b))
    conn.commit()
    conn.close()
