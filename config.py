import os

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads/images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
DATABASE_NAME = 'articles.db' 