from __future__ import annotations

from typing import List, Optional
from dataclasses import asdict

from .dto import NoteDTO
from .repo_interface import NoteRepository
from .sqlite_repo import SQLiteNoteRepository


class NoteService:
    def __init__(self, repo: NoteRepository):
        self._repo = repo

    def add_note(self, dto: NoteDTO) -> NoteDTO:
        return self._repo.add_note(dto)

    def get_note(self, note_id: str) -> Optional[NoteDTO]:
        return self._repo.get_note(note_id)

    def update_note(self, dto: NoteDTO) -> Optional[NoteDTO]:
        return self._repo.update_note(dto)

    def delete_note(self, note_id: str) -> bool:
        return self._repo.delete_note(note_id)

    def list_notes(self, notebook: Optional[str] = None, tag: Optional[str] = None) -> List[NoteDTO]:
        return self._repo.list_notes(notebook=notebook, tag=tag)

    def search_notes(self, query: str) -> List[NoteDTO]:
        return self._repo.search_notes(query)

    def list_notebooks(self) -> List[str]:
        return self._repo.list_notebooks()
