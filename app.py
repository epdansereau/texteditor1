import base64
import hashlib
import sqlite3
from flask import Flask, render_template, request, jsonify
from cryptography.fernet import Fernet, InvalidToken

app = Flask(__name__)
DB_PATH = 'documents.db'
# Token used for dummy decrypts to keep timing consistent.
DUMMY_TOKEN = Fernet(Fernet.generate_key()).encrypt(b'0')


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

    key = derive_key(filename, password)
    f = Fernet(key)
    token = row[0] if row else DUMMY_TOKEN

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
