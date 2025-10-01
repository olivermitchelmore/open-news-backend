import os
import re
import sqlite3
from datetime import datetime, timezone
from unicodedata import normalize
from werkzeug.utils import secure_filename
from config import DATABASE_NAME


def create_slug(text):
    text = normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)


def init_db():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                slug TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author TEXT NOT NULL,
                image_filename TEXT,
                description TEXT,
                category TEXT,
                published TEXT
            )
        ''')
        # databases created before these columns existed
        for column in ('description', 'category', 'published'):
            try:
                cursor.execute(f"ALTER TABLE articles ADD COLUMN {column} TEXT")
            except sqlite3.OperationalError:
                pass
        cursor.execute("UPDATE articles SET published = ? WHERE published IS NULL",
                       (datetime.now(timezone.utc).isoformat(),))
        conn.commit()
        print("Database initialized")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()


def insert_article(title, content, author, upload_folder, image=None, description=None, category=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        base_slug = create_slug(title)
        unique_slug = base_slug
        counter = 1

        while True:
            cursor.execute("SELECT slug FROM articles WHERE slug = ?", (unique_slug,))
            if cursor.fetchone() is None:
                break
            unique_slug = f"{base_slug}-{counter}"
            counter += 1

        image_filename = None
        if image and image.filename:
            _, extension = os.path.splitext(image.filename)
            image_filename = secure_filename(f"{unique_slug}{extension}")
            filepath = os.path.join(upload_folder, image_filename)
            image.save(filepath)

        cursor.execute('''
            INSERT INTO articles (slug, title, content, author, image_filename, description, category, published)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (unique_slug, title, content, author, image_filename, description, category,
              datetime.now(timezone.utc).isoformat()))
        conn.commit()
        print(f"Article '{title}' inserted with slug: {unique_slug}")
        return unique_slug
    except sqlite3.Error as e:
        print(f"Error inserting article: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def delete_article_by_slug(slug):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT image_filename FROM articles WHERE slug = ?", (slug,))
        article_data = cursor.fetchone()

        if article_data is None:
            return None, 0

        image_filename = article_data['image_filename']

        cursor.execute("DELETE FROM articles WHERE slug = ?", (slug,))
        rows_deleted = cursor.rowcount
        conn.commit()

        return image_filename, rows_deleted
    except sqlite3.Error as e:
        print(f"Error deleting article: {e}")
        conn.rollback()
        return None, 0
    finally:
        conn.close()


def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_articles():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT slug, title, content, author, image_filename, description, category, published FROM articles")
        articles = cursor.fetchall()
        return [dict(article) for article in articles]
    finally:
        conn.close()


def get_article_by_slug(slug):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE slug = ?", (slug,))
        article = cursor.fetchone()
        return article
    finally:
        conn.close()

