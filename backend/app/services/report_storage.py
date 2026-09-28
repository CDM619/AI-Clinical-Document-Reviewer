
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


# Store the database in the backend directory, not inside venv.
BACKEND_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BACKEND_DIR / "clinical_reports.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS clinical_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                input_type TEXT NOT NULL,
                character_count INTEGER NOT NULL,
                report_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def save_report(
    report: dict,
    input_type: str,
    character_count: int,
    filename: str | None = None,
) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    report_json = json.dumps(report, ensure_ascii=False)

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO clinical_reports (
                filename,
                input_type,
                character_count,
                report_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                filename,
                input_type,
                character_count,
                report_json,
                created_at,
            ),
        )

        return cursor.lastrowid


def get_report_by_id(report_id: int):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, filename, input_type, character_count,
                   report_json, created_at
            FROM clinical_reports
            WHERE id = ?
            """,
            (report_id,),
        ).fetchone()

    if row is None:
        return None

    return {
        "id": row["id"],
        "filename": row["filename"],
        "input_type": row["input_type"],
        "character_count": row["character_count"],
        "report": json.loads(row["report_json"]),
        "created_at": row["created_at"],
    }


def get_report_history(limit: int = 50):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, filename, input_type, character_count, created_at
            FROM clinical_reports
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "filename": row["filename"],
            "input_type": row["input_type"],
            "character_count": row["character_count"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]