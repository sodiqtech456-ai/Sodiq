import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import pickle

# Configuration
SECRET_KEY = 'replace-this-with-a-random-secret'  # Change for production!
DB_PATH = 'users.db'

# Model loading
MODEL_PATH = 'model.pkl'
VECTORIZER_PATH = 'vectorizer.pkl'
model = pickle.load(open(MODEL_PATH, 'rb'))
vectorizer = pickle.load(open(VECTORIZER_PATH, 'rb'))

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

init_db()

def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"msg": "Username and password required"}), 400
    if get_user(username):
        return jsonify({"msg": "User already exists"}), 409
    hashed = generate_password_hash(password)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
    conn.commit()
    conn.close()
    return jsonify({"msg": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"msg": "Username and password required"}), 400
    user = get_user(username)
    if not user or not check_password_hash(user[2], password):
        return jsonify({"msg": "Invalid credentials"}), 401
    token = jwt.encode({
        'user_id': user[0],
        'username': user[1],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token})

def authenticate(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:
        return None

@app.route("/predict", methods=["POST"])
def predict():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"msg": "Missing or invalid token"}), 401
    token = auth.split()[1]
    user = authenticate(token)
    if not user:
        return jsonify({"msg": "Invalid token"}), 401
    data = request.json
    news_text = data.get('news')
    if not news_text:
        return jsonify({"msg": "No news text supplied"}), 400
    X = vectorizer.transform([news_text])
    prediction = model.predict(X)[0]
    label = "Fake" if prediction == 1 else "Real"
    return jsonify({"result": label})

if __name__ == "__main__":
    app.run(debug=True)