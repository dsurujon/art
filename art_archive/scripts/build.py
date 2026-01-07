import csv
import sqlite3
from pathlib import Path
from PIL import Image

ROOT = Path()
DB_PATH = ROOT / "db" / "archive.db"
ORIGINALS = ROOT / "originals"
DERIVATIVES = ROOT / "derivatives"
METADATA = ROOT / "metadata" / "metadata.csv"

WEB_SIZE = 2400
THUMB_SIZE = 600


def init_db(conn):
    """
    Initialize the database schema
    One table for artworks, and one for individual images
    """
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS artwork (
        id INTEGER PRIMARY KEY,
        slug TEXT UNIQUE,
        title TEXT,
        year INTEGER,
        medium TEXT,
        width_in REAL,
        height_in REAL,
        is_available BOOLEAN,
        description TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY,
        artwork_id INTEGER,
        role TEXT,
        path TEXT,
        width_px INTEGER,
        height_px INTEGER,
        FOREIGN KEY (artwork_id) REFERENCES artwork(id)
    )
    """)
    cur.execute("""
    CREATE TABLE tags (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    );
                """)
    cur.execute("""
    CREATE TABLE artwork_tags (
        artwork_id INTEGER,
        tag_id INTEGER,
        PRIMARY KEY (artwork_id, tag_id)
    );
    """)
                 
    conn.commit()
    print("Database initialized.")


def insert_artwork(conn, row):
    """
    For each row on the metadata table, insert a new artwork entry
    """
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO artwork
        (slug, title, year, medium, width_in, height_in, is_available, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["slug"],
        row["title"],
        row["year"] or None,
        row["medium"],
        row["width_in"],
        row["height_in"],
        row["is_available"].lower() == "true",
        row["description"]
    ))
    conn.commit()
    cur.execute("SELECT id FROM artwork WHERE slug = ?", (row["slug"],))
    return cur.fetchone()[0]


def make_derivative(img, size, out_path):
    """
    Create a derivative image with the specified size and save it to the given path.
    """
    out = img.copy()
    out.thumbnail((size, size))
    out.save(out_path, quality=90)
    return out.size


def register_image(conn, artwork_id, role, path, size):
    """
    Register a derivative image in the database 
    """
    conn.execute("""
        INSERT INTO images (artwork_id, role, path, width_px, height_px)
        VALUES (?, ?, ?, ?, ?)
    """, (artwork_id, role, str(path), size[0], size[1]))
    conn.commit()


def process_artwork(conn, row):
    slug = row["slug"]
    master_path = ORIGINALS / slug / "main.JPEG"
    if not master_path.exists():
        print(f"Missing master for {slug}")
        return
    art_dir = DERIVATIVES / slug
    art_dir.mkdir(parents=True, exist_ok=True)
    # Load master image
    img = Image.open(master_path).convert("RGB")
    artwork_id = insert_artwork(conn, row)
    # web derivative
    web_path = art_dir / "web_2400px.jpg"
    web_size = make_derivative(img, WEB_SIZE, web_path)
    register_image(conn, artwork_id, "web", web_path, web_size)
    # thumbnail
    thumb_path = art_dir / "thumb_600px.jpg"
    thumb_size = make_derivative(img, THUMB_SIZE, thumb_path)
    register_image(conn, artwork_id, "thumbnail", thumb_path, thumb_size)


def main():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    with open(METADATA, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            process_artwork(conn, row)

    conn.close()
    print("Build complete.")


if __name__ == "__main__":
    main()
