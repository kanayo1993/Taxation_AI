import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app


def test_add_and_list():
    client = app.test_client()
    resp = client.get('/api/delinquents')
    assert resp.status_code == 200
    assert resp.get_json() == []

    resp = client.post('/api/delinquents', json={'name': 'A', 'amount': 1000, 'due_date': '2024-01-01'})
    assert resp.status_code == 201

    resp = client.get('/api/delinquents')
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'A'

    resp = client.post('/api/delinquents/1/pay')
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'paid'
