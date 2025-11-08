from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# File to store expenses
DATA_FILE = 'expenses.json'

def load_expenses():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_expenses(expenses):
    with open(DATA_FILE, 'w') as f:
        json.dump(expenses, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    expenses = load_expenses()
    return jsonify(expenses)

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.json
    expenses = load_expenses()
    
    expense = {
        'id': len(expenses) + 1,
        'description': data.get('description'),
        'amount': float(data.get('amount')),
        'category': data.get('category'),
        'date': data.get('date', datetime.now().strftime('%Y-%m-%d'))
    }
    
    expenses.append(expense)
    save_expenses(expenses)
    
    return jsonify(expense), 201

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    expenses = load_expenses()
    expenses = [e for e in expenses if e['id'] != expense_id]
    save_expenses(expenses)
    return jsonify({'message': 'Expense deleted'}), 200

@app.route('/api/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    data = request.json
    expenses = load_expenses()
    
    for expense in expenses:
        if expense['id'] == expense_id:
            expense['description'] = data.get('description', expense['description'])
            expense['amount'] = float(data.get('amount', expense['amount']))
            expense['category'] = data.get('category', expense['category'])
            expense['date'] = data.get('date', expense['date'])
            break
    
    save_expenses(expenses)
    return jsonify({'message': 'Expense updated'}), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    expenses = load_expenses()
    
    if not expenses:
        return jsonify({
            'total': 0,
            'by_category': {},
            'recent_count': 0
        })
    
    total = sum(e['amount'] for e in expenses)
    by_category = {}
    
    for expense in expenses:
        category = expense['category']
        by_category[category] = by_category.get(category, 0) + expense['amount']
    
    return jsonify({
        'total': total,
        'by_category': by_category,
        'recent_count': len(expenses)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)