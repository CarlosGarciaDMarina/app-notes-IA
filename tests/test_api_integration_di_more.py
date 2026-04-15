import os
import tempfile
from pathlib import Path
import pytest

def test_api_integration_di_more_basic():
    import notesorg.api as api
    app = api.create_app()
    client = app.test_client()
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tempdb = tf.name
    os.environ['NOTESORG_DB_FILE'] = tempdb
    try:
        # Create
        r = client.post('/notes', json={"title": "DI More", "content": "more", "notebook": "UI", "tags": ["more"]})
        assert r.status_code == 201
        id = r.get_json().get('id')
        assert id
        # List notebooks
        r = client.get('/notebooks')
        assert r.status_code == 200
        # Search
        r = client.get('/search?query=more')
        assert r.status_code in (200, 304)
    finally:
        try:
            os.remove(tempdb)
        except Exception:
            pass
        del os.environ['NOTESORG_DB_FILE']
