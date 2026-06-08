import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "company.db"

SCHEMA = """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    annual_leave_days INTEGER NOT NULL
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    owner_department TEXT NOT NULL
);

INSERT INTO employees (name, department, annual_leave_days) VALUES
    ('Sara', 'Engineering', 20),
    ('Omar', 'HR', 22);

INSERT INTO projects (name, owner_department) VALUES
    ('RAG Platform', 'Engineering');
"""

if __name__ == "__main__":
    connection = sqlite3.connect(DB_PATH)
    connection.executescript(SCHEMA)
    connection.commit()
    connection.close()
    print(f"Created {DB_PATH}")
