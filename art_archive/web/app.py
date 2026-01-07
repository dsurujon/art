from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "archive.db"
DERIVATIVES = ROOT / "derivatives"

app = FastAPI()
templates = Jinja2Templates(directory=ROOT / "web" / "templates")

app.mount("/static", StaticFiles(directory=ROOT / "web" / "static"), name="static")
app.mount("/images", StaticFiles(directory=DERIVATIVES), name="images")


def db():
    return sqlite3.connect(DB_PATH)


@app.get("/", response_class=HTMLResponse)
def gallery(request: Request, tag: str | None = None):
    conn = db()
    cur = conn.cursor()

    if tag:
        cur.execute("""
            SELECT DISTINCT a.id, a.slug, a.title
            FROM artwork a
            JOIN artwork_tags at ON a.id = at.artwork_id
            JOIN tags t ON at.tag_id = t.id
            WHERE t.name = ?
            ORDER BY a.year DESC
        """, (tag,))
    else:
        cur.execute("""
            SELECT id, slug, title
            FROM artwork
            ORDER BY year DESC
        """)

    artworks = cur.fetchall()

    cur.execute("SELECT name FROM tags ORDER BY name")
    tags = [r[0] for r in cur.fetchall()]

    conn.close()

    return templates.TemplateResponse(
        "gallery.html",
        {
            "request": request,
            "artworks": artworks,
            "tags": tags,
            "active_tag": tag
        }
    )


@app.get("/artwork/{slug}", response_class=HTMLResponse)
def artwork_detail(request: Request, slug: str):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title, medium, year, description
        FROM artwork WHERE slug = ?
    """, (slug,))
    art = cur.fetchone()

    cur.execute("""
        SELECT t.name
        FROM tags t
        JOIN artwork_tags at ON t.id = at.tag_id
        WHERE at.artwork_id = ?
    """, (art[0],))
    tags = [r[0] for r in cur.fetchall()]

    conn.close()

    return templates.TemplateResponse(
        "artwork.html",
        {
            "request": request,
            "art": art,
            "slug": slug,
            "tags": tags
        }
    )
