import sqlite3
import json
import os
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional


DATA_DIR = os.path.expanduser("~/.notesorg")
DB_FILE = os.environ.get("NOTESORG_DB_FILE", os.path.join(DATA_DIR, "notes.db"))


def _current_iso() -> str:
    return datetime.utcnow().isoformat()


@dataclass
class Note:
    id: str
    title: str
    content: str
    created_at: str
    updated_at: str
    tags: List[str]
    notebook: Optional[str] = None


def _get_connection():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS notes ("
        "id TEXT PRIMARY KEY, "
        "title TEXT, "
        "content TEXT, "
        "created_at TEXT, "
        "updated_at TEXT, "
        "notebook TEXT, "
        "tags TEXT)"
    )
    conn.commit()
    return conn


def add_note(title: str, content: str, notebook: Optional[str] = None, tags: Optional[List[str]] = None) -> Note:
    conn = _get_connection()
    now = _current_iso()
    note_id = str(uuid.uuid4())
    tags_list = tags or []
    conn.execute(
        "INSERT INTO notes (id, title, content, created_at, updated_at, notebook, tags) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (note_id, title, content, now, now, notebook, json.dumps(tags_list)),
    )
    conn.commit()
    conn.close()
    return Note(id=note_id, title=title, content=content, created_at=now, updated_at=now, notebook=notebook, tags=tags_list)


def _row_to_note(row) -> Note:
    id_, title, content, created_at, updated_at, notebook, tags_json = row
    tags = json.loads(tags_json) if tags_json else []
    return Note(id=id_, title=title, content=content, created_at=created_at, updated_at=updated_at, notebook=notebook, tags=tags)


def find_note(note_id: str) -> Optional[Note]:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, created_at, updated_at, notebook, tags FROM notes WHERE id=?", (note_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return _row_to_note(row)


def update_note(note_id: str, **kwargs) -> Optional[Note]:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, created_at, updated_at, notebook, tags FROM notes WHERE id=?", (note_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    existing = _row_to_note(row)
    title = kwargs.get("title", existing.title)
    content = kwargs.get("content", existing.content)
    notebook = kwargs.get("notebook", existing.notebook)
    tags = kwargs.get("tags", existing.tags)
    updated_at = _current_iso()
    cur.execute(
        "UPDATE notes SET title=?, content=?, notebook=?, tags=?, updated_at=? WHERE id=?",
        (title, content, notebook, json.dumps(tags), updated_at, note_id),
    )
    conn.commit()
    conn.close()
    return Note(id=note_id, title=title, content=content, created_at=existing.created_at, updated_at=updated_at, notebook=notebook, tags=tags)


def delete_note(note_id: str) -> bool:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id=?", (note_id,))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def list_notes(notebook: Optional[str] = None, tag: Optional[str] = None) -> List[Note]:
    conn = _get_connection()
    cur = conn.cursor()
    sql = "SELECT id, title, content, created_at, updated_at, notebook, tags FROM notes"
    clauses = []
    params = []
    if notebook:
        clauses.append("notebook = ?")
        params.append(notebook)
    if tag:
        # tags stored as JSON array text
        clauses.append("tags LIKE ?")
        params.append(f'%"{tag}"%')
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [_row_to_note(r) for r in rows]


def search_notes(query: str) -> List[Note]:
    conn = _get_connection()
    cur = conn.cursor()
    q = f"%{query.lower()}%"
    cur.execute(
        "SELECT id, title, content, created_at, updated_at, notebook, tags FROM notes WHERE LOWER(title) LIKE ? OR LOWER(content) LIKE ?",
        (q, q),
    )
    rows = cur.fetchall()
    conn.close()
    return [_row_to_note(r) for r in rows]


def list_notebooks() -> List[str]:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT notebook FROM notes WHERE notebook IS NOT NULL")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]
