from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

records = []
next_id = 1

@app.route('/')
def index():
    return render_template('index.html')

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
            'status': 'unpaid'
        }
        records.append(record)
        next_id += 1
        return jsonify(record), 201
    return jsonify(records)

@app.route('/api/delinquents/<int:record_id>/pay', methods=['POST'])
def mark_paid(record_id):
    for record in records:
        if record['id'] == record_id:
            record['status'] = 'paid'
            return jsonify(record)
    return jsonify({'error': 'Record not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
