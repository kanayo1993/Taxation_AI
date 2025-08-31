from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# In-memory storage for demo purposes
records = []
payments = []
next_id = 1

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/business')
def business_page():
    return render_template('business.html')

@app.route('/api/delinquents', methods=['GET', 'POST'])
def handle_delinquents():
    global next_id
    if request.method == 'POST':
        data = request.get_json()
        record = {
            'id': next_id,
            'name': data['name'],
            'amount': data['amount'],
            'due_date': data['due_date'],
            'status': 'unpaid',
            'note': data.get('note', ''),
            'important': data.get('important', False)
        }
        records.append(record)
        next_id += 1
        return jsonify(record), 201
    return jsonify(records)


@app.route('/api/payments/import', methods=['POST'])
def import_payments():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Expected a list'}), 400
    payments.extend(data)
    return jsonify({'imported': len(data)}), 201


@app.route('/api/business/<name>/unpaid')
def business_unpaid(name):
    result = [p for p in payments
              if p.get('tax_type') == 'individual_resident_special'
              and p.get('business') == name
              and p.get('status') == 'unpaid']
    return jsonify(result)

@app.route('/api/delinquents/<int:record_id>/pay', methods=['POST'])
def mark_paid(record_id):
    for record in records:
        if record['id'] == record_id:
            record['status'] = 'paid'
            return jsonify(record)
    return jsonify({'error': 'Record not found'}), 404


@app.route('/api/delinquents/<int:record_id>/flag', methods=['POST'])
def flag_record(record_id):
    for record in records:
        if record['id'] == record_id:
            record['important'] = True
            note = request.get_json(silent=True) or {}
            if 'note' in note:
                record['note'] = note['note']
            return jsonify(record)
    return jsonify({'error': 'Record not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
