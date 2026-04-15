## DTOs (Notas) - capa de DTOs

- Propósito: Transferir datos entre capas sin exponer estructuras internas.
- Objetos pequeños: NotaDTO, NotebookDTO, TagDTO.
- NotaDTO: id, title, content, created_at, updated_at, notebook, tags.
- NotebookDTO: name, created_at (opcional).
- TagDTO: name.

Notas: este archivo documenta el contrato de datos entre capa de presentación y negocio, y entre negocio y repositorio.
