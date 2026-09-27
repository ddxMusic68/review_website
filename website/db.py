import sqlite3
from pathlib import Path

from .models import Review, StarRating, YtVideo

DB_PATH = Path(__file__).resolve().parent.parent / "reviews.db"


def connect():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                stars INTEGER
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS category_reviews (
                video_id TEXT NOT NULL,
                category TEXT NOT NULL,
                review TEXT NOT NULL,
                stars INTEGER NOT NULL,
                PRIMARY KEY (video_id, category),
                FOREIGN KEY (video_id) REFERENCES videos(video_id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS video_metadata (
                video_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                thumbnail TEXT NOT NULL,
                published_at TEXT NOT NULL
            )
            """
        )

        columns = {
            row[1] for row in conn.execute("PRAGMA table_info(video_metadata)")
        }
        for column, definition in {
            "views": "INTEGER",
            "likes": "INTEGER",
            "comments": "INTEGER",
            "duration": "TEXT",
            "is_short": "INTEGER",
        }.items():
            if column not in columns:
                conn.execute(
                    f"ALTER TABLE video_metadata ADD COLUMN {column} {definition}"
                )


def save_video(video: YtVideo):
    if video.star_review is None:
        raise ValueError("video.star_review is required to save")

    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO videos (video_id, stars) VALUES (?, ?)",
            (video.video_id, video.star_review.stars),
        )
        for category in video.review.categories.values():
            rating = int(category.rating.stars) if category.rating else 0
            conn.execute(
                """
                INSERT OR REPLACE INTO category_reviews (video_id, category, review, stars)
                VALUES (?, ?, ?, ?)
                """,
                (video.video_id, category.name, category.review, rating),
            )


def get_video(video_id: str):
    with connect() as conn:
        conn.row_factory = sqlite3.Row
        video_row = conn.execute(
            "SELECT * FROM videos WHERE video_id = ?", (video_id,)
        ).fetchone()
        if video_row is None:
            return None

        review = Review.default()
        rows = conn.execute(
            "SELECT * FROM category_reviews WHERE video_id = ?", (video_id,)
        ).fetchall()
        for row in rows:
            category = review.categories[row["category"]]
            category.review = row["review"]
            category.rating = StarRating(stars=row["stars"])

        return YtVideo(
            video_id=video_row["video_id"],
            star_review=StarRating(stars=video_row["stars"]),
            review=review,
        )


def get_all_videos():
    with connect() as conn:
        videos = conn.execute(
            "SELECT video_id, stars FROM videos"
        ).fetchall()
    return {(row[0], row[1]) for row in videos}


def has_video(video_id: str):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT 1 FROM video_metadata WHERE video_id = ?", (video_id,)
        ).fetchone()
    return row is not None


def save_video_metadata(video_id, title, thumbnail, published_at):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO video_metadata (video_id, title, thumbnail, published_at)
            VALUES (?, ?, ?, ?)
            """,
            (video_id, title, thumbnail, published_at),
        )


def update_video_stats(video_id, views, likes, comments, duration):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            UPDATE video_metadata
            SET views = ?, likes = ?, comments = ?, duration = ?
            WHERE video_id = ?
            """,
            (views, likes, comments, duration, video_id),
        )


def update_video_short(video_id, is_short):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE video_metadata SET is_short = ? WHERE video_id = ?",
            (1 if is_short else 0, video_id),
        )


def get_all_video_ids(missing_short_only=False):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        if missing_short_only:
            rows = conn.execute(
                "SELECT video_id FROM video_metadata WHERE is_short IS NULL"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT video_id FROM video_metadata"
            ).fetchall()
    return [row[0] for row in rows]


def get_saved_videos():
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM video_metadata ORDER BY published_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]