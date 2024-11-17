#database API
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'accounts.db'

# Helper to interact with the database
def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# Endpoint to fetch ready accounts
@app.route('/accounts', methods=['GET'])
def get_accounts():
    status = request.args.get('status', 'ready')
    accounts = query_db("SELECT * FROM accounts WHERE status = ?", [status])
    return jsonify([dict(acc) for acc in accounts])

# Endpoint to mark an account as sold
@app.route('/sell/<int:account_id>', methods=['POST'])
def sell_account(account_id):
    query_db("UPDATE accounts SET status = 'sold' WHERE id = ?", [account_id])
    return jsonify({"success": True, "message": f"Account {account_id} marked as sold."})

# Endpoint to delete an account
@app.route('/delete/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    query_db("DELETE FROM accounts WHERE id = ?", [account_id])
    return jsonify({"success": True, "message": f"Account {account_id} deleted."})

# Endpoint to add a new account
@app.route('/add', methods=['POST'])
def add_account():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')
    points = data.get('points', 0)
    referrer = data.get('referrer')
    referrals = data.get('referrals', '')
    unique_code = data.get('unique_code')

    if not all([email, password, phone, points, referrer, unique_code]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # Insert the new account into the database
    query_db("INSERT INTO accounts (email, password, phone, date_added, points, referrer, referrals, unique_code, status) VALUES (?, ?, ?, datetime('now'), ?, ?, ?, ?, ?)", 
             [email, password, phone, points, referrer, referrals, unique_code, 'ready'])

    return jsonify({"success": True, "message": "Account added successfully."})

# Endpoint for authentication (simple PIN-based)
@app.route('/auth', methods=['POST'])
def authenticate():
    pin = request.json.get('pin')
    if pin == "YOUR_SECURE_PIN":
        return jsonify({"success": True, "token": "YOUR_GENERATED_JWT_TOKEN"})
    return jsonify({"success": False, "message": "Unauthorized"}), 401

if __name__ == '__main__':
    app.run(debug=True)
