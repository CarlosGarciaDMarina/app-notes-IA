import os
import tempfile
from pathlib import Path

import pytest

def test_api_integration_di_basic():
    # Ensure we can import API and run with a temp DB
    import notesorg.api as api
    app = api.create_app()
    client = app.test_client()

    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tempdb = tf.name
    os.environ['NOTESORG_DB_FILE'] = tempdb
    try:
        # Create a note
        resp = client.post('/notes', json={"title": "DI Note", "content": "content", "notebook": "DI", "tags": ["test"]})
        assert resp.status_code == 201
        data = resp.get_json()
        note_id = data.get('id')
        assert note_id is not None

        # List notes
        resp = client.get('/notes')
        assert resp.status_code == 200
        notes = resp.get_json()
        assert isinstance(notes, list)

        # Get by id
        resp = client.get(f'/notes/{note_id}')
        assert resp.status_code == 200

        # Update
        resp = client.put(f'/notes/{note_id}', json={"title": "DI Note Updated"})
        assert resp.status_code == 200

        # Delete
        resp = client.delete(f'/notes/{note_id}')
        assert resp.status_code in (200, 204, 202)
    finally:
        try:
            os.remove(tempdb)
        except Exception:
            pass
        del os.environ['NOTESORG_DB_FILE']
