import importlib
import os
from pathlib import Path


def test_sqlite_crud(tmp_path, monkeypatch):
    db_path = tmp_path / "notes.db"
    monkeypatch.setenv("NOTESORG_DB_FILE", str(db_path))
    import notesorg.core as core
    importlib.reload(core)

    n = core.add_note("Title1", "Content1", notebook="Work", tags=["tag1"])
    assert n.title == "Title1"

    notes = core.list_notes()
    assert any(x.id == n.id for x in notes)

    updated = core.update_note(n.id, title="Title1 Updated")
    assert updated is not None
    assert updated.title == "Title1 Updated"

    found = core.search_notes("Content1")
    assert any(x.id == n.id for x in found)

    ok = core.delete_note(n.id)
    assert ok
    assert core.find_note(n.id) is None


def test_list_notebooks(tmp_path, monkeypatch):
    db_path = tmp_path / "notes2.db"
    monkeypatch.setenv("NOTESORG_DB_FILE", str(db_path))
    import notesorg.core as core
    importlib.reload(core)
    core.add_note("N1", "C1", notebook="Personal")
    core.add_note("N2", "C2", notebook="Work")
    core.add_note("N3", "C3")
    nb = set(core.list_notebooks())
    assert nb == {"Personal", "Work"}
