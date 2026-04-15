"""NotesOrg API - refactored para usar la capa de negocio (NoteService).
EndPoints se conservan: /notes, /notes/{id}, /notebooks, /search
Este module expone una simple DI para el servicio de negocio usando SQLite como repositorio.
"""

from __future__ import annotations

from flask import Flask, jsonify, request
from dataclasses import asdict

from notesorg.dto import NoteDTO
from notesorg.sqlite_repo import SQLiteNoteRepository
from notesorg.service import NoteService
from notesorg.repo_interface import NoteRepository

_service: NoteService | None = None


def _get_service() -> NoteService:
    global _service
    if _service is None:
        repo: NoteRepository = SQLiteNoteRepository()
        _service = NoteService(repo)
    return _service


def _note_to_dict(n: NoteDTO) -> dict:
    return asdict(n)


def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="/static")

    @app.route("/")
    def index():  # simple placeholder landing
        try:
            from flask import render_template
            return render_template("index.html")
        except Exception:
            return ("<!doctype html>""<html lang='es'>"
                    "<head><meta charset='utf-8'>"
                    "<title>NotesOrg</title></head>"
                    "<body style='font-family: Arial, sans-serif; padding: 20px;'>"
                    "<h1>NotesOrg</h1>"
                    "<p>Interfaz mínima disponible. Usa la API para gestionar notas.</p>"
                    "</body></html>")

    @app.route("/notes", methods=["GET", "POST"])
    def notes():
        svc = _get_service()
        if request.method == "GET":
            notebook = request.args.get("notebook")
            tag = request.args.get("tag")
            dtos = svc.list_notes(notebook=notebook, tag=tag)
            return jsonify([_note_to_dict(n) for n in dtos])
        data = request.get_json(force=True) or {}
        title = data.get("title")
        content = data.get("content", "")
        notebook = data.get("notebook")
        tags = data.get("tags", [])
        if not title:
            return jsonify({"error": "title required"}), 400
        dto = NoteDTO(title=title, content=content, notebook=notebook, tags=tags)
        created = svc.add_note(dto)
        return jsonify(_note_to_dict(created)), 201

    @app.route("/notes/<note_id>", methods=["GET", "PUT", "DELETE"])
    def note_by_id(note_id):
        svc = _get_service()
        if request.method == "GET":
            dto = svc.get_note(note_id)
            if not dto:
                return jsonify({"error": "not found"}), 404
            return jsonify(_note_to_dict(dto))
        if request.method == "PUT":
            data = request.get_json(force=True) or {}
            existing = svc.get_note(note_id)
            if not existing:
                return jsonify({"error": "not found"}), 404
            dto = NoteDTO(id=note_id,
                          title=data.get("title", existing.title),
                          content=data.get("content", existing.content),
                          notebook=data.get("notebook", existing.notebook),
                          tags=data.get("tags", existing.tags))
            updated = svc.update_note(dto)
            return jsonify(_note_to_dict(updated))
        if svc.delete_note(note_id):
            return jsonify({"message": "deleted"})
        return jsonify({"error": "not found"}), 404

    @app.route("/notebooks", methods=["GET"])
    def notebooks():
        svc = _get_service()
        return jsonify(svc.list_notebooks())

    @app.route("/search", methods=["GET"])
    def search():
        svc = _get_service()
        q = request.args.get("query", "")
        return jsonify([_note_to_dict(n) for n in svc.search_notes(q)])

    return app


def main():  # pragma: no cover
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":  # pragma: no cover
    main()
