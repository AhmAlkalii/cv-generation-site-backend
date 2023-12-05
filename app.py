from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import sqlite3
from openai import OpenAI

app = Flask(__name__)
CORS(app)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json

    # Validate required fields
    required_fields = ['firstname', 'lastname', 'email', 'mobile', 'gender', 'pwd']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # Validate email uniqueness
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (data['email'],))
        existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({'error': 'Email is already registered'}), 400

    # Hash the password before storing it
    hashed_password = hash_password(data['pwd'])

    # Create a user object and add it to the users table
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (firstname, lastname, email, mobile, gender, hashed_password)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['firstname'], data['lastname'], data['email'], data['mobile'], data['gender'], hashed_password))
        conn.commit()

    return jsonify({'message': 'Registration successful'})

@app.route('/login', methods=['POST'])
def login_user():
    data = request.json

    # Validate required fields
    required_fields = ['email', 'pwd']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # Check if the user exists
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (data['email'],))
        user = cursor.fetchone()

    if user:
        # Check if the provided password matches the hashed password in the database
        hashed_password = hash_password(data['pwd'])
        if hashed_password == user[6]:  # Assuming hashed_password is at index 6
            return jsonify({'message': 'Login successful'})
        else:
            return jsonify({'error': 'Invalid password'}), 401
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/openai-api-key', methods=['GET'])
def get_openai_api_key():
    # Replace 'YOUR_OPENAI_API_KEY' with the actual OpenAI API key
    openai_api_key = 'Provide-API-key-Here'
    return jsonify({'openai_api_key': openai_api_key})

if __name__ == '__main__':
    app.run(debug=True)
