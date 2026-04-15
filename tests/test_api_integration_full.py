import os
import json
import tempfile
import pytest
from pathlib import Path

def test_api_integration_full():
    # Ensure the API can be instantiated with a temp DB and exercised
    import notesorg.api as api_module
    from flask import json as flask_json
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tempdb = tf.name
    os.environ['NOTESORG_DB_FILE'] = tempdb
    try:
        app = api_module.create_app()
        client = app.test_client()
        # create
        resp = client.post('/notes', json={"title": "UI Note", "content": "content", "notebook": "UI", "tags": ["test"]})
        assert resp.status_code == 201
        data = resp.get_json()
        note_id = data.get('id')
        assert note_id
        # list
        resp = client.get('/notes')
        assert resp.status_code == 200
        # get by id
        resp = client.get(f'/notes/{note_id}')
        assert resp.status_code == 200
        # update
        resp = client.put(f'/notes/{note_id}', json={"title": "UI Note Updated"})
        assert resp.status_code == 200
        # delete
        resp = client.delete(f'/notes/{note_id}')
        assert resp.status_code in (200, 204, 202)
    finally:
        try:
            os.remove(tempdb)
        except Exception:
            pass
        if 'NOTESORG_DB_FILE' in os.environ:
            del os.environ['NOTESORG_DB_FILE']
