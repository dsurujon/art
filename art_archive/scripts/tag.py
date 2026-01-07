import sqlite3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "archive.db"
DERIVATIVES = ROOT / "derivatives"  # used to open web image if available


def connect():
    return sqlite3.connect(DB_PATH)


def get_artworks(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, slug, title, medium, year
        FROM artwork
        ORDER BY year, title
    """)
    return cur.fetchall()


def get_tags_for_artwork(conn, artwork_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT t.name
        FROM tags t
        JOIN artwork_tags at ON t.id = at.tag_id
        WHERE at.artwork_id = ?
        ORDER BY t.name
    """, (artwork_id,))
    return [r[0] for r in cur.fetchall()]


def open_image(slug):
    img = DERIVATIVES / slug / "web_2400px.jpg"
    if not img.exists():
        return

    try:
        if sys.platform == "darwin":
            subprocess.run(["open", img])
        elif sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", img])
        elif sys.platform.startswith("win"):
            subprocess.run(["start", img], shell=True)
    except Exception:
        pass


def ensure_tag(conn, name):
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
    conn.commit()

    cur.execute("SELECT id FROM tags WHERE name = ?", (name,))
    return cur.fetchone()[0]


def add_tag(conn, artwork_id, tag_name):
    tag_id = ensure_tag(conn, tag_name)
    conn.execute("""
        INSERT OR IGNORE INTO artwork_tags (artwork_id, tag_id)
        VALUES (?, ?)
    """, (artwork_id, tag_id))
    conn.commit()


def remove_tag(conn, artwork_id, tag_name):
    cur = conn.cursor()
    cur.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
    row = cur.fetchone()
    if not row:
        return

    tag_id = row[0]
    conn.execute("""
        DELETE FROM artwork_tags
        WHERE artwork_id = ? AND tag_id = ?
    """, (artwork_id, tag_id))
    conn.commit()


def prompt():
    print("\nCommands:")
    print("  add:    comma,separated,tags")
    print("  rm:     comma,separated,tags")
    print("  skip:   move on")
    print("  quit:   exit\n")
    return input("> ").strip()


def main():
    conn = connect()
    artworks = get_artworks(conn)

    if not artworks:
        print("No artworks found.")
        return

    for artwork_id, slug, title, medium, year in artworks:
        print("\n" + "=" * 60)
        print(f"{title or '(untitled)'}")
        print(f"{slug} | {medium or ''} | {year or ''}")

        open_image(slug)

        tags = get_tags_for_artwork(conn, artwork_id)
        print("\nCurrent tags:", ", ".join(tags) if tags else "(none)")

        while True:
            cmd = prompt()

            if not cmd or cmd.lower() == "skip":
                break

            if cmd.lower() == "quit":
                conn.close()
                print("Exiting.")
                return

            if cmd.startswith("add:"):
                names = [t.strip().lower() for t in cmd[4:].split(",") if t.strip()]
                for name in names:
                    add_tag(conn, artwork_id, name)
                tags = get_tags_for_artwork(conn, artwork_id)
                print("Updated tags:", ", ".join(tags))

            elif cmd.startswith("rm:"):
                names = [t.strip().lower() for t in cmd[3:].split(",") if t.strip()]
                for name in names:
                    remove_tag(conn, artwork_id, name)
                tags = get_tags_for_artwork(conn, artwork_id)
                print("Updated tags:", ", ".join(tags))

            else:
                print("Unrecognized command.")

    conn.close()
    print("\nTagging complete.")


if __name__ == "__main__":
    main()
