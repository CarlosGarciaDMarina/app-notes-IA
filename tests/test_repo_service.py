from __future__ import annotations

import os
from pathlib import Path
import pytest

from notesorg.dto import NoteDTO
from notesorg.sqlite_repo import SQLiteNoteRepository
from notesorg.service import NoteService


def test_repo_service_basic(tmp_path):
    db_path = tmp_path / "notes.db"
    repo = SQLiteNoteRepository(str(db_path))
    service = NoteService(repo)

    dto = NoteDTO(title="Test Note", content="contenido", notebook="Test", tags=["tag1"])
    created = service.add_note(dto)
    assert created.title == "Test Note"
    assert created.id is not None

    all_notes = service.list_notes()
    assert len(all_notes) == 1

    note = service.get_note(created.id)
    assert note is not None
    assert note.title == "Test Note"

    updated = service.update_note(NoteDTO(id=created.id, title="Test Note Updated"))
    assert updated is not None
    assert updated.title == "Test Note Updated"

    ok = service.delete_note(created.id)
    assert ok
    assert service.get_note(created.id) is None

def test_list_notebooks(tmp_path):
    db_path = tmp_path / "notes2.db"
    repo = SQLiteNoteRepository(str(db_path))
    service = NoteService(repo)
    service.add_note(NoteDTO(title="A", content="a", notebook=" Personal"))
    service.add_note(NoteDTO(title="B", content="b", notebook="Work"))
    nb = set(service.list_notebooks())
    assert nb == {" Personal", "Work"}
