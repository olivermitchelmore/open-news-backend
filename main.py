from flask import Flask, jsonify, request, send_from_directory, abort
import os
from werkzeug.utils import secure_filename
import bleach
import markdown2
from database.database_manager import get_article_by_slug, insert_article, init_db, get_all_articles, delete_article_by_slug
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/articles', methods=['GET'])
def get_articles():
    articles = get_all_articles()
    return jsonify(articles)

@app.route('/articles', methods=['POST'])
def create_article():
    title = request.form.get('title')
    text = request.form.get('article_content')
    author = request.form.get('author-name')
    description = request.form.get('description')
    category = request.form.get('category')

    if not all([title, text, author]):
        abort(400, description="Missing required fields: title, article_content, or author-name.")

    clean_title = bleach.clean(title)
    clean_author = bleach.clean(author)
    clean_description = bleach.clean(description) if description else None
    clean_category = bleach.clean(category).strip().lower() if category else None
    
    html_content = markdown2.markdown(text)
    clean_content = bleach.clean(html_content, tags=list(bleach.sanitizer.ALLOWED_TAGS) + ['h1', 'h2', 'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a'])

    image = request.files.get('ArticleImage')
    
    if image and not allowed_file(image.filename):
        abort(400, description="Invalid image file type.")

    insert_article(clean_title, clean_content, clean_author, app.config['UPLOAD_FOLDER'], image, clean_description, clean_category)

    return "created successfully", 201

@app.route('/articles/<string:slug>')
def getarticle(slug):
    article = get_article_by_slug(slug)
    if article is None:
        abort(404, description="Article not found")

    return jsonify(dict(article))


@app.route('/articles/<string:image_name>/image')
def get_article_image(image_name):
    print("retreiving image from image name: ", image_name)
    return send_from_directory(app.config['UPLOAD_FOLDER'], image_name)

@app.route('/articles/<string:slug>', methods=['DELETE'])
def delete_article(slug):
    image_filename, rows_deleted = delete_article_by_slug(slug)

    if rows_deleted == 0:
        abort(404, description="Article not found")

    if image_filename:
        try:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        except OSError as e:
            print(f"Error deleting image file {image_filename}: {e}")

    return jsonify({"message": f"Article '{slug}' deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)