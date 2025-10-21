def test_health(client):
    r = client.get('/api/health')
    assert r.status_code == 200 and r.get_json()['status'] == 'ok'
