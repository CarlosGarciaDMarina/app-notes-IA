import argparse
from typing import List, Optional

from .core import (
    add_note,
    delete_note,
    find_note,
    list_notes,
    list_notebooks,
    search_notes,
    update_note,
)


def _print_note(n) -> None:
    print(f"ID: {n.id}")
    print(f"Title: {n.title}")
    print(f"Notebook: {n.notebook}")
    print(f"Tags: {', '.join(n.tags) if n.tags else ''}")
    print(f"Created: {n.created_at}")
    print(f"Updated: {n.updated_at}")
    print("Content:")
    print(n.content)
    print("-" * 40)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="notesorg", description="Notas organizadas por cuadernos y etiquetas.")
    subparsers = parser.add_subparsers(dest="cmd", help="Comando"
)

    # Add note
    p_add = subparsers.add_parser("add", help="Añadir una nueva nota")
    p_add.add_argument("--title", required=True, help="Título de la nota")
    p_add.add_argument("--content", required=True, help="Contenido de la nota")
    p_add.add_argument("--notebook", help="Cuaderno al que pertenece la nota")
    p_add.add_argument("--tags", nargs="*", help="Etiquetas para la nota")

    # List notes
    p_list = subparsers.add_parser("list", help="Listar notas")
    p_list.add_argument("--notebook", help="Filtrar por cuaderno")
    p_list.add_argument("--tag", help="Filtrar por etiqueta")

    # Show search
    p_search = subparsers.add_parser("search", help="Buscar en notas")
    p_search.add_argument("--query", required=True, help="Término de búsqueda")

    # Notebooks
    p_nb = subparsers.add_parser("notebooks", help="Listar cuadernos existentes")

    # Show / edit / delete
    p_show = subparsers.add_parser("show", help="Mostrar una nota por ID")
    p_show.add_argument("--id", required=True, help="ID de la nota")
    p_edit = subparsers.add_parser("edit", help="Editar una nota existente")
    p_edit.add_argument("--id", required=True, help="ID de la nota")
    p_edit.add_argument("--title")
    p_edit.add_argument("--content")
    p_edit.add_argument("--notebook")
    p_edit.add_argument("--tags", nargs="*")
    p_delete = subparsers.add_parser("delete", help="Eliminar una nota")
    p_delete.add_argument("--id", required=True, help="ID de la nota")

    args = parser.parse_args(argv)

    if args.cmd == "add":
        note = add_note("title".strip() or args.title, args.content, args.notebook, args.tags or [])
        print(f"Nota creada: {note.id}")
        return 0
    if args.cmd == "list":
        notes = list_notes(notebook=args.notebook, tag=args.tag)
        for n in notes:
            print(f"[{n.id}] {n.title} ({n.notebook}) - {', '.join(n.tags)}")
        return 0
    if args.cmd == "search":
        results = search_notes(args.query)
        for n in results:
            print(f"[{n.id}] {n.title}")
        return 0
    if args.cmd == "notebooks":
        for nb in list_notebooks():
            print(nb)
        return 0
    if args.cmd == "show":
        n = find_note(args.id)
        if not n:
            print("Nota no encontrada")
            return 1
        _print_note(n)
        return 0
    if args.cmd == "edit":
        updates = {}
        if args.title is not None:
            updates["title"] = args.title
        if args.content is not None:
            updates["content"] = args.content
        if args.notebook is not None:
            updates["notebook"] = args.notebook
        if args.tags is not None:
            updates["tags"] = args.tags
        updated = update_note(args.id, **updates)
        if updated:
            print("Notas actualizada correctamente")
            _print_note(updated)
            return 0
        print("No se pudo actualizar la nota")
        return 1
    if args.cmd == "delete":
        if delete_note(args.id):
            print("Nota eliminada")
            return 0
        print("Nota no encontrada")
        return 1

    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
