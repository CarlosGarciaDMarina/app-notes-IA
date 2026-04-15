from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .dto import NoteDTO


class NoteRepository(ABC):
    @abstractmethod
    def add_note(self, dto: NoteDTO) -> NoteDTO: ...

    @abstractmethod
    def get_note(self, note_id: str) -> Optional[NoteDTO]: ...

    @abstractmethod
    def update_note(self, dto: NoteDTO) -> Optional[NoteDTO]: ...

    @abstractmethod
    def delete_note(self, note_id: str) -> bool: ...

    @abstractmethod
    def list_notes(self, notebook: Optional[str] = None, tag: Optional[str] = None) -> List[NoteDTO]: ...

    @abstractmethod
    def search_notes(self, query: str) -> List[NoteDTO]: ...

    @abstractmethod
    def list_notebooks(self) -> List[str]: ...
