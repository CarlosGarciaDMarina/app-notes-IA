from __future__ import annotations

import json
import sqlite3
import os
from datetime import datetime
from typing import List, Optional

from .dto import NoteDTO
from .repo_interface import NoteRepository


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


class SQLiteNoteRepository(NoteRepository):
    def __init__(self, db_path: Optional[str] = None):
        self._db_path = db_path or os.environ.get("NOTESORG_DB_FILE", os.path.join(os.path.expanduser("~"), ".notesorg", "notes.db"))
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._ensure_schema()

    def _ensure_schema(self):
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                  id TEXT PRIMARY KEY,
                  title TEXT,
                  content TEXT,
                  created_at TEXT,
                  updated_at TEXT,
                  notebook TEXT,
                  tags TEXT
                )
                """
            )
            conn.commit()

    def _row_to_dto(self, row) -> NoteDTO:
        id_, title, content, created_at, updated_at, notebook, tags_json = row
        tags = json.loads(tags_json) if tags_json else []
        return NoteDTO(id=id_, title=title, content=content, created_at=created_at, updated_at=updated_at, notebook=notebook, tags=tags)

    def _dto_to_row(self, dto: NoteDTO):
        return (
            dto.id or self._generate_id(),
            dto.title,
            dto.content,
            dto.created_at or _now_iso(),
            dto.updated_at or _now_iso(),
            dto.notebook,
            json.dumps(dto.tags or []),
        )

    def _generate_id(self) -> str:
        import uuid
        return str(uuid.uuid4())

    def add_note(self, dto: NoteDTO) -> NoteDTO:
        if not dto.id:
            dto.id = self._generate_id()
        if not dto.created_at:
            dto.created_at = _now_iso()
        dto.updated_at = _now_iso()
        row = self._dto_to_row(dto)
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO notes (id, title, content, created_at, updated_at, notebook, tags) VALUES (?, ?, ?, ?, ?, ?, ?)",
                row,
            )
            conn.commit()
        return dto

    def get_note(self, note_id: str) -> Optional[NoteDTO]:
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, title, content, created_at, updated_at, notebook, tags FROM notes WHERE id = ?", (note_id,))
            row = cur.fetchone()
        return self._row_to_dto(row) if row else None

    def update_note(self, dto: NoteDTO) -> Optional[NoteDTO]:
        if not dto.id:
            return None
        dto.updated_at = _now_iso()
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE notes SET title=?, content=?, notebook=?, tags=?, updated_at=? WHERE id=?",
                (dto.title, dto.content, dto.notebook, json.dumps(dto.tags or []), dto.updated_at, dto.id),
            )
            conn.commit()
        return dto

    def delete_note(self, note_id: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            return cur.rowcount > 0

    def list_notes(self, notebook: Optional[str] = None, tag: Optional[str] = None) -> List[NoteDTO]:
        sql = "SELECT id, title, content, created_at, updated_at, notebook, tags FROM notes"
        params = []
        if notebook or tag:
            clauses = []
            if notebook:
                clauses.append("notebook = ?")
                params.append(notebook)
            if tag:
                clauses.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            sql += " WHERE " + " AND ".join(clauses)
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
        return [self._row_to_dto(r) for r in rows]

    def search_notes(self, query: str) -> List[NoteDTO]:
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.cursor()
            q = f"%{query.lower()}%"
            cur.execute(
                "SELECT id, title, content, created_at, updated_at, notebook, tags FROM notes WHERE LOWER(title) LIKE ? OR LOWER(content) LIKE ?",
                (q, q),
            )
            rows = cur.fetchall()
        return [self._row_to_dto(r) for r in rows]

    def list_notebooks(self) -> List[str]:
        with sqlite3.connect(self._db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT notebook FROM notes WHERE notebook IS NOT NULL AND notebook != ''")
            rows = cur.fetchall()
        return [r[0] for r in rows if r[0]]
