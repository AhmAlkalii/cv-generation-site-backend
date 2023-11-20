from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import sqlite3
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# Set your OpenAI API key
openai_client = OpenAI(api_key='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')

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

# @app.route('/generate-cv', methods=['POST'])
# def generate_cv():
#     data = request.json
#
#     # Validate required fields
#     required_fields = ['jobDescription']
#     for field in required_fields:
#         if field not in data:
#             return jsonify({'error': f'Missing required field: {field}'}), 400
#
#     # Call the OpenAI API for CV generation
#     try:
#         response = openai_client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": data['jobDescription']},
#             ]
#         )
#         generated_cv = response.choices[0].message['content'].strip()
#
#         return jsonify({'generatedCV': generated_cv})
#     except Exception as e:
#         print(e)
#         return jsonify({'error': 'CV generation failed'}), 500

@app.route('/generate-cv', methods=['POST'])
def generate_cv():
    data = request.json

    # Validate required fields
    required_fields = ['jobDescription']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # Call the OpenAI API for CV generation
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": data['jobDescription']},
            ]
        )

        # Print or log the response
        print(response)

        # Check if 'choices' is present and is a list
        if 'choices' in response and isinstance(response['choices'], list) and response['choices']:
            # Check if the first element is a dictionary
            first_choice = response['choices'][0]
            if isinstance(first_choice, dict) and 'message' in first_choice:
                generated_cv = first_choice['message']['content'].strip()
                return jsonify({'generatedCV': generated_cv})
            else:
                return jsonify({'error': 'Unexpected response structure'}), 500
        else:
            return jsonify({'error': 'Unexpected response structure'}), 500

    except Exception as e:
        print(e)
        return jsonify({'error': 'CV generation failed'}), 500

if __name__ == '__main__':
    app.run(debug=True)
