"""Exercise both APIs against a temporary copy of the submitted database."""
import importlib.util
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

with tempfile.TemporaryDirectory() as directory:
    database = Path(directory) / 'database.db'
    shutil.copy2(ROOT / 'activity2/lab5_api/database.db', database)
    sys.path.insert(0, str(ROOT / 'activity2/lab5_api'))
    import db
    db.connect_to_db = lambda: sqlite3.connect(database)
    api = load('lab5_app', ROOT / 'activity2/lab5_api/app.py').app.test_client()
    names_module = load('names_app', ROOT / 'activity2/users_api/app.py')
    names_module.DATABASE = database
    names = names_module.app.test_client()
    assert api.get('/api/users').get_json() == []
    assert names.get('/get_users').get_json() == []
    identifiers = []
    for name in ['Ali Rida Awad', 'Test User']:
        payload = dict(name=name, email='test@example.com', phone='000', address='Test', country='Lebanon')
        response = api.post('/api/users/add', json=payload)
        assert response.status_code == 200, response.data
        identifiers.append(response.get_json()['user_id'])
    assert names.get('/get_users').get_json() == ['Ali Rida Awad', 'Test User']
    user = api.get(f'/api/users/{identifiers[0]}').get_json()
    user['name'] = 'Updated User'
    assert api.put('/api/users/update', json=user).get_json()['name'] == 'Updated User'
    assert names.get('/get_users').get_json() == ['Updated User', 'Test User']
    assert api.delete(f'/api/users/delete/{identifiers[0]}').status_code == 200
    assert names.get('/get_users').get_json() == ['Test User']
    assert names.post('/get_users').status_code == 405
    hello = load('hello_app', ROOT / 'activity1/hello/app.py').app.test_client()
    assert hello.get('/').data == b'Hello, World!\n'
print('PASS: hello; Lab 5 create/list/read/update/delete; database-backed names; empty database; GET-only route.')
print('Temporary test data removed. Submitted database unchanged. Docker execution is a separate check.')
