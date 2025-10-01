# Open News backend

A small Flask API for storing and serving news articles. Articles are written in Markdown, converted to sanitised HTML and kept in a SQLite database, with an optional image per article.

This is an old, unfinished personal project. It is published as it was left, not as a finished product. It has no authentication and runs with Flask's debug server, so it should not be exposed to the internet.

It is the back end for [open-news-frontend](https://github.com/olivermitchelmore/open-news-frontend), an Astro site that builds its pages from this API.

## Running

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

The API listens on `http://127.0.0.1:5000`. The database (`articles.db`) and the image folder (`uploads/images`) are created on first run.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/articles` | List all articles |
| `POST` | `/articles` | Create an article (multipart form) |
| `GET` | `/articles/<slug>` | Get one article |
| `DELETE` | `/articles/<slug>` | Delete an article and its image |
| `GET` | `/articles/<image_filename>/image` | Get an article's image |

### Creating an article

Form fields:

| Field | Required | Notes |
| --- | --- | --- |
| `title` | yes | The slug is generated from this |
| `article_content` | yes | Markdown |
| `author-name` | yes | |
| `description` | no | Short summary |
| `category` | no | the front end uses `world`, `politics`, `business`, `technology`, `science`, `culture` and `sport` |
| `ArticleImage` | no | png, jpg, jpeg, gif or webp |

```bash
curl -F title="Example headline" \
     -F article_content="Some **Markdown** text." \
     -F author-name="A. Writer" \
     -F category=world \
     -F ArticleImage=@photo.jpg \
     http://127.0.0.1:5000/articles
```

### Article format

```json
{
  "slug": "example-headline",
  "title": "Example headline",
  "content": "<p>Some <strong>Markdown</strong> text.</p>\n",
  "author": "A. Writer",
  "image_filename": "example-headline.jpg",
  "description": null,
  "category": "world",
  "published": "2025-09-04T09:30:00+00:00"
}
```
