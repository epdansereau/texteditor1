import base64
import hashlib
import sqlite3
from flask import Flask, render_template, request, jsonify
from cryptography.fernet import Fernet, InvalidToken

app = Flask(__name__)
DB_PATH = 'documents.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'CREATE TABLE IF NOT EXISTS documents (filename TEXT PRIMARY KEY, content BLOB)'
    )
    return conn


def derive_key(filename: str, password: str) -> bytes:
    """Derive a Fernet key from the filename and password."""
    digest = hashlib.sha256((filename + password).encode()).digest()
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
    cur.execute('SELECT content FROM documents WHERE filename=?', (filename,))
    row = cur.fetchone()
    conn.close()
    if not row:
        # New document
        return jsonify({'content': ''})
    key = derive_key(filename, password)
    f = Fernet(key)
    try:
        decrypted = f.decrypt(row[0]).decode()
    except InvalidToken:
        return jsonify({'error': 'Invalid file name or password'}), 403
    return jsonify({'content': decrypted})


@app.post('/api/save')
def save_doc():
    data = request.get_json()
    filename = data.get('filename', '')
    password = data.get('password', '')
    content = data.get('content', '')
    if not filename or not password:
        return jsonify({'error': 'Filename and password required'}), 400

    key = derive_key(filename, password)
    f = Fernet(key)
    encrypted = f.encrypt(content.encode())

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        'INSERT OR REPLACE INTO documents (filename, content) VALUES (?, ?)',
        (filename, encrypted),
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'saved'})


if __name__ == '__main__':
    app.run(debug=True)
