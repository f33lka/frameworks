from conftest import j

def test_login_success(client):
    code, data = j(client.post('/api/auth/login', json={'email':'admin@example.com','password':'admin123'}))
    assert code == 200 and 'access_token' in data

def test_login_fail(client):
    code, _ = j(client.post('/api/auth/login', json={'email':'admin@example.com','password':'wrong'}))
    assert code == 401
