from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class NoteDTO:
    id: Optional[str] = None
    title: str = ""
    content: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    notebook: Optional[str] = None
    tags: List[str] = None


@dataclass
class NotebookDTO:
    name: str
    created_at: Optional[str] = None


@dataclass
class TagDTO:
    name: str
