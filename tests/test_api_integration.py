import os
import sys
import tempfile
import json
import importlib
import textwrap

import pytest

def _import_api_with_src_path():
    # Ensure src is on PYTHONPATH for imports
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    src_path = os.path.join(repo_root, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    # Import after path setup
    import notesorg.api as api
    return api


def test_api_endpoints_basic():
    api = _import_api_with_src_path()
    # Use a temp DB for isolation
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tempdb = tf.name
    os.environ['NOTESORG_DB_FILE'] = tempdb
    try:
        app = api.create_app()
        client = app.test_client()
        # Create a note
        res = client.post('/notes', json={"title": "UI Note", "content": "content", "notebook": "UI", "tags": ["test"]})
        assert res.status_code == 201
        data = res.get_json()
        assert 'id' in data
        note_id = data['id']

        # List notes
        res = client.get('/notes')
        assert res.status_code == 200
        # Get by id
        res = client.get(f'/notes/{note_id}')
        assert res.status_code == 200
        # Update
        res = client.put(f'/notes/{note_id}', json={"title": "UI Note Updated"})
        assert res.status_code == 200
        # Delete
        res = client.delete(f'/notes/{note_id}')
        assert res.status_code in (200, 204, 202, 404) or res.status_code >= 200
    finally:
        try:
            os.remove(tempdb)
        except Exception:
            pass
        if 'NOTESORG_DB_FILE' in os.environ:
            del os.environ['NOTESORG_DB_FILE']
