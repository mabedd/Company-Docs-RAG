from __future__ import annotations

import sqlite3
from pathlib import Path

from pypdf import PdfReader


def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_pdf_file(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def load_sql_schema(db_path: Path) -> str:
    connection = sqlite3.connect(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        sections: list[str] = []
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            column_lines = ", ".join(f"{col[1]} ({col[2]})" for col in columns)
            sections.append(f"Table {table}: {column_lines}")
        return "\n".join(sections)
    finally:
        connection.close()
