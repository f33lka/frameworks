from conftest import token, j

def test_integration_create_and_close_defect(client):
    t = token(client)
    # create project
    code, proj = j(client.post('/api/projects', json={'name':'FlowProj'}, headers={'Authorization': f'Bearer {t}'}))
    assert code == 201
    # create defect
    code, d = j(client.post('/api/defects', json={'project_id': proj['id'], 'title':'A'},
                            headers={'Authorization': f'Bearer {t}'}))
    assert code == 201
    # move to closed
    for s in ['in_progress','in_review','closed']:
        code, _ = j(client.patch(f"/api/defects/{d['id']}/status", json={'status': s},
                                 headers={'Authorization': f'Bearer {t}'}))
        assert code == 200
