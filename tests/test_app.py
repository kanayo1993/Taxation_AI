import sys, os, pytest
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import app as app_module

app = app_module.app


@pytest.fixture(autouse=True)
def reset_state():
    app_module.records.clear()
    app_module.payments.clear()
    app_module.next_id = 1


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


def test_note_and_flag():
    client = app.test_client()
    resp = client.post('/api/delinquents', json={'name': 'B', 'amount': 500, 'due_date': '2024-02-01', 'note': '重要'})
    assert resp.status_code == 201
    record_id = resp.get_json()['id']

    resp = client.post(f'/api/delinquents/{record_id}/flag')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['important'] is True

    resp = client.get('/api/delinquents')
    data = resp.get_json()
    assert data[0]['note'] == '重要'


def test_import_and_business_unpaid():
    client = app.test_client()
    payload = [
        {
            'tax_type': 'individual_resident_special',
            'business': 'ABC商事',
            'period': '2024-01',
            'amount': 1000,
            'status': 'unpaid'
        },
        {
            'tax_type': 'property',
            'payer': '山田太郎',
            'period': '2024',
            'amount': 2000,
            'status': 'paid'
        }
    ]
    resp = client.post('/api/payments/import', json=payload)
    assert resp.status_code == 201
    assert resp.get_json()['imported'] == 2

    # imported payments should not create delinquent records
    resp = client.get('/api/delinquents')
    assert resp.get_json() == []

    resp = client.get('/api/business/ABC商事/unpaid')
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]['period'] == '2024-01'
