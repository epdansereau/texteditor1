import base64
import os
import sqlite3
from flask import Flask, render_template, request, jsonify
from cryptography.fernet import Fernet, InvalidToken
from argon2.low_level import hash_secret_raw, Type

app = Flask(__name__)
DB_PATH = 'documents.db'
# Token used for dummy decrypts to keep timing consistent.
DUMMY_TOKEN = Fernet(Fernet.generate_key()).encrypt(b'0')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'CREATE TABLE IF NOT EXISTS documents (filename TEXT PRIMARY KEY, salt BLOB, content BLOB)'
    )
    return conn


SALT_SIZE = 16
DEFAULT_SALT = b"\x00" * SALT_SIZE


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet key from the password and salt using Argon2."""
    digest = hash_secret_raw(
        password.encode(),
        salt,
        time_cost=2,
        memory_cost=65536,
        parallelism=2,
        hash_len=32,
        type=Type.ID,
    )
    return base64.urlsafe_b64encode(digest)


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/api/open')
def open_doc():
    data = request.get_json()
    filename = data.get('filename', '')
    password = data.get('password', '')
    if not filename or not password:
        return jsonify({'error': 'Filename and password required'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT salt, content FROM documents WHERE filename=?', (filename,))
    row = cur.fetchone()
    conn.close()

    salt, token = row if row else (DEFAULT_SALT, DUMMY_TOKEN)

    key = derive_key(password, salt)
    f = Fernet(key)

    content = ""
    try:
        content = f.decrypt(token).decode()
    except InvalidToken:
        pass

    # Dummy decrypt to keep timing consistent whether the document exists or
    # the password is wrong.
    try:
        f.decrypt(DUMMY_TOKEN)
    except InvalidToken:
        pass

    return jsonify({'content': content})


@app.post('/api/save')
def save_doc():
    data = request.get_json()
    filename = data.get('filename', '')
    password = data.get('password', '')
    content = data.get('content', '')
    if not filename or not password:
        return jsonify({'error': 'Filename and password required'}), 400

    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(content.encode())

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        'INSERT OR REPLACE INTO documents (filename, salt, content) VALUES (?, ?, ?)',
        (filename, salt, encrypted),
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'saved'})


if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() in ('1', 'true', 't', 'yes')
    app.run(debug=debug_mode)
