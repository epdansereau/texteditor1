# Secure Text Editor

A basic privacy‑focused text editor that stores documents encoded in a SQLite database. Each document is protected by a file name and password pair. Keys are derived using Argon2 with a unique random salt per file.

## Features
- Create or open documents using a file name and password.
- Text is encrypted and saved in a local SQLite database.
- Save current document or save under a new file name and password.
- Basic editing features with a plain text area.

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python app.py
   ```
3. In your browser open `http://localhost:5000`.
4. Enter a file name and password to create or open a document. After opening, the fields are cleared and the editor becomes available.
5. Use **Save** to store changes or **Save As** to save under a different name and password.

The database file `documents.db` is created in the working directory. Without the correct file name and password a document cannot be opened.
