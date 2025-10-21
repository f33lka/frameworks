from conftest import token, j

def test_defects_flow(client):
    t = token(client)
    # need any project id
    r = client.get('/api/projects', headers={'Authorization': f'Bearer {t}'})
    pid = r.get_json()[0]['id']
    # create defect
    code, data = j(client.post('/api/defects', json={'project_id': pid, 'title':'Проблема', 'priority':'high'},
                               headers={'Authorization': f'Bearer {t}'}))
    assert code == 201
    did = data['id']
    # wrong transition
    code, _ = j(client.patch(f'/api/defects/{did}/status', json={'status':'closed'},
                             headers={'Authorization': f'Bearer {t}'}))
    assert code == 409
    # correct transitions
    for s in ['in_progress','in_review','closed']:
        code, _ = j(client.patch(f'/api/defects/{did}/status', json={'status': s},
                                 headers={'Authorization': f'Bearer {t}'}))
        assert code == 200
