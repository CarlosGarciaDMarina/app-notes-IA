"""notesorg: un organizador de notas sencillo en Python.

Este paquete expone una API mínima para gestionar notas en un backend JSON
local y una CLI para crear, listar, buscar y organizar notas por cuadernos
(notebooks) y etiquetas (tags).
"""

from . import core  # noqa: F401

__all__ = ["core"]
