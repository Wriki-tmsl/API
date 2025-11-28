import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'user': 'tranzsilica',
    'password': 'tranzsilica1$',
    'host': '127.0.0.1',
    'database': 'library',
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def xor_crypt(data, key='my_secret_key'):
    # Simple XOR encoding/decoding
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

# --- User APIs ---
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, is_librarian, is_admin FROM members")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    encoded_password = xor_crypt(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM members WHERE email=%s", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Email already registered.'}), 400
    cursor.execute(
        "INSERT INTO members (name, email, password, is_librarian, is_admin) VALUES (%s, %s, %s, %s, %s)",
        (name, email, encoded_password, 0, 0)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'User created successfully.'})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'User deleted successfully.'})

@app.route('/api/users/<int:user_id>/make-librarian', methods=['POST'])
def make_librarian(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE members SET is_librarian=1 WHERE id=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'User promoted to librarian.'})

@app.route('/api/users/<int:user_id>/remove-librarian', methods=['PUT'])
def remove_librarian(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE members SET is_librarian=0 WHERE id=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Librarian role removed.'})

# --- Book APIs ---
@app.route('/api/books', methods=['GET'])
def get_books():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(books)

@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.json
    title = data.get('title')
    author = data.get('author')
    isbn = data.get('isbn')
    quantity = data.get('quantity')
    library = data.get('library', 'Central Library')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO books (title, author, isbn, library, quantity) VALUES (%s, %s, %s, %s, %s)",
        (title, author, isbn, library, quantity)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Book added successfully.'})

@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    title = data.get('title')
    author = data.get('author')
    isbn = data.get('isbn')
    quantity = data.get('quantity')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE books SET title=%s, author=%s, isbn=%s, quantity=%s WHERE id=%s",
        (title, author, isbn, quantity, book_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Book updated successfully.'})

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def remove_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id=%s", (book_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Book removed successfully.'})

# --- Wishlist APIs ---
@app.route('/api/wishlist/<int:user_id>', methods=['GET'])
def get_wishlist(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.id, b.title, b.author
        FROM wishlists w
        JOIN books b ON w.book_id = b.id
        WHERE w.user_id = %s
    """, (user_id,))
    wishlist_books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(wishlist_books)

@app.route('/api/wishlist/<int:user_id>', methods=['POST'])
def add_to_wishlist(user_id):
    data = request.json
    book_id = data.get('book_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO wishlists (user_id, book_id) VALUES (%s, %s)", (user_id, book_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Book added to wishlist.'})

@app.route('/api/wishlist/<int:user_id>/<int:book_id>', methods=['DELETE'])
def remove_from_wishlist(user_id, book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wishlists WHERE user_id=%s AND book_id=%s", (user_id, book_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Book removed from wishlist.'})

# --- Transactions APIs ---
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(transactions)

# --- Member APIs ---
@app.route('/api/members', methods=['GET'])
def get_members():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email FROM members")
    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(members)

@app.route('/api/members', methods=['POST'])
def add_member():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO members (name, email) VALUES (%s, %s)", (name, email))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Member added successfully.'})

@app.route('/api/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    data = request.json
    name = data.get('name')
    email = data.get('email')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE members SET name=%s, email=%s WHERE id=%s", (name, email, member_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Member updated successfully.'})

@app.route('/api/members/<int:member_id>', methods=['DELETE'])
def remove_member(member_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id=%s", (member_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Member removed successfully.'})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, password, is_librarian, is_admin FROM members WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user and xor_crypt(password) == user['password']:
        user.pop('password')
        return jsonify(user)
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True, port=5001)