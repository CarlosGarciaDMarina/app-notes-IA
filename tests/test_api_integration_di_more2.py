import os
import tempfile
from pathlib import Path
import pytest

def _setup_client_with_tempdb():
    import notesorg.api as api
    app = api.create_app()
    client = app.test_client()
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tempdb = tf.name
    os.environ['NOTESORG_DB_FILE'] = tempdb
    return client, tempdb

def test_missing_title_di():
    client, tempdb = _setup_client_with_tempdb()
    try:
        resp = client.post('/notes', json={"content": "no title"})
        assert resp.status_code == 400
    finally:
        os.remove(tempdb)
        del os.environ['NOTESORG_DB_FILE']

def test_get_not_found_di():
    client, tempdb = _setup_client_with_tempdb()
    try:
        resp = client.get('/notes/nonexistent-id')
        assert resp.status_code == 404
    finally:
        os.remove(tempdb)
        del os.environ['NOTESORG_DB_FILE']

def test_update_not_found_di():
    client, tempdb = _setup_client_with_tempdb()
    try:
        resp = client.put('/notes/nonexistent-id', json={"title": "x"})
        assert resp.status_code == 404
    finally:
        os.remove(tempdb)
        del os.environ['NOTESORG_DB_FILE']

def test_delete_not_found_di():
    client, tempdb = _setup_client_with_tempdb()
    try:
        resp = client.delete('/notes/nonexistent-id')
        assert resp.status_code == 404
    finally:
        os.remove(tempdb)
        del os.environ['NOTESORG_DB_FILE']
