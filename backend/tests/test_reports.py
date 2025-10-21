from conftest import token

def test_report_summary(client):
    t = token(client)
    r = client.get('/api/reports/summary', headers={'Authorization': f'Bearer {t}'})
    assert r.status_code == 200
    data = r.get_json()
    assert 'total' in data and 'by_status' in data
