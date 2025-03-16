from flask import Flask, request, jsonify, session
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/users_db"
app.config['SECRET_KEY'] = 'secret_key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'

mongo = PyMongo(app)
mail = Mail(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = generate_password_hash(data.get('password'))
    user = mongo.db.users.find_one({'username': username})
    if user:
        return jsonify({'message': 'Username already exists!'}), 400
    mongo.db.users.insert_one({'username': username, 'email': email, 'password': password})
    return jsonify({'message': 'Registration successful!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = mongo.db.users.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        session['username'] = username
        return jsonify({'message': 'Login successful!'}), 200
    return jsonify({'message': 'Invalid credentials!'}), 401

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    user = mongo.db.users.find_one({'email': email})
    if user:
        msg = Message('Password Reset', sender='your_email@gmail.com', recipients=[email])
        msg.body = 'Click the link to reset your password.'
        mail.send(msg)
        return jsonify({'message': 'Reset link sent!'}), 200
    return jsonify({'message': 'Email not found!'}), 404

@app.route('/contacts', methods=['POST'])
def save_contact():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.json
    contact = {
        'username': session['username'],
        'phone': data.get('phone'),
        'email': data.get('email'),
        'address': data.get('address'),
        'reg_no': data.get('reg_no')
    }
    mongo.db.contacts.insert_one(contact)
    return jsonify({'message': 'Contact saved!'}), 201

@app.route('/search', methods=['GET'])
def search():
    reg_no = request.args.get('reg_no')
    contact = mongo.db.contacts.find_one({'reg_no': reg_no})
    if contact:
        contact.pop('_id')
        return jsonify(contact), 200
    return jsonify({'message': 'Contact not found!'}), 404

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
