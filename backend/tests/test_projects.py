from conftest import token

def test_projects_crud(client):
    t = token(client)
    # list
    r = client.get('/api/projects', headers={'Authorization': f'Bearer {t}'})
    assert r.status_code == 200
    # create (manager)
    r = client.post('/api/projects', json={'name':'Новый проект'}, headers={'Authorization': f'Bearer {t}'})
    assert r.status_code == 201
    pid = r.get_json()['id']
    # update
    r = client.put(f'/api/projects/{pid}', json={'description':'upd'}, headers={'Authorization': f'Bearer {t}'})
    assert r.status_code == 200
    # delete
    r = client.delete(f'/api/projects/{pid}', headers={'Authorization': f'Bearer {t}'})
    assert r.status_code == 200
