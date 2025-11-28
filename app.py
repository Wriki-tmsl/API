import requests
from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__, template_folder='src/components', static_folder='src/styles')
app.secret_key = 'your_secret_key'  # Change this to a secure random value in production

API_BASE = 'http://127.0.0.1:5001/api'

# --- Mock Data for fallback/demo ---
mock_user = {
    "name": "Jane Smith",
    "membership_id": "789012",
    "borrowed_books": [
        {"title": "1984", "library": "Central Library", "due": "2024-09-15"},
        {"title": "Pride and Prejudice", "library": "Community Library", "due": "2024-09-20"}
    ],
    "transactions": [
        {"date": "2024-08-01", "book": "1984", "library": "Central Library", "status": "Borrowed"},
        {"date": "2024-07-15", "book": "The Hobbit", "library": "Community Library", "status": "Returned"}
    ]
}

# --- Routes for Dynamic Pages ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user-profile')
def user_profile():
    return render_template('user-profile.html', user=mock_user)

@app.route('/book-catalogue')
def book_catalogue():
    try:
        resp = requests.get(f"{API_BASE}/books")
        books = resp.json()
    except Exception:
        books = []
    return render_template('book-catalogue.html', books=books)

@app.route('/librarian-dashboard')
def librarian_dashboard():
    if not session.get('user_id') or not session.get('is_librarian'):
        return redirect(url_for('book_catalogue'))
    try:
        resp = requests.get(f"{API_BASE}/transactions")
        transactions = resp.json()
    except Exception:
        transactions = []
    return render_template('librarian-dashboard.html', transactions=transactions)

@app.route('/add-book', methods=['POST'])
def add_book():
    data = {
        "title": request.form.get('title'),
        "author": request.form.get('author'),
        "isbn": request.form.get('isbn'),
        "quantity": request.form.get('quantity'),
        "library": "Central Library"
    }
    resp = requests.post(f"{API_BASE}/books", json=data)
    msg = resp.json().get('message', 'Error adding book.')
    return render_dashboard(book_message=msg)

@app.route('/update-book', methods=['POST'])
def update_book_form():
    book_id = request.form.get('id')
    data = {
        "title": request.form.get('title'),
        "author": request.form.get('author'),
        "isbn": request.form.get('isbn'),
        "quantity": request.form.get('quantity')
    }
    resp = requests.put(f"{API_BASE}/books/{book_id}", json=data)
    msg = resp.json().get('message', 'Error updating book.')
    return render_dashboard(book_message=msg)

@app.route('/remove-book', methods=['POST'])
def remove_book():
    book_id = request.form.get('id')
    resp = requests.delete(f"{API_BASE}/books/{book_id}")
    msg = resp.json().get('message', 'Error removing book.')
    return render_dashboard(book_message=msg)

@app.route('/add-member', methods=['POST'])
def add_member():
    data = {
        "name": request.form.get('name'),
        "email": request.form.get('email')
    }
    resp = requests.post(f"{API_BASE}/members", json=data)
    msg = resp.json().get('message', 'Error adding member.')
    return render_dashboard(member_message=msg)

@app.route('/update-member', methods=['POST'])
def update_member_form():
    member_id = request.form.get('id')
    data = {
        "name": request.form.get('name'),
        "email": request.form.get('email')
    }
    resp = requests.put(f"{API_BASE}/members/{member_id}", json=data)
    msg = resp.json().get('message', 'Error updating member.')
    return render_dashboard(member_message=msg)

@app.route('/remove-member', methods=['POST'])
def remove_member():
    member_id = request.form.get('id')
    resp = requests.delete(f"{API_BASE}/members/{member_id}")
    msg = resp.json().get('message', 'Error removing member.')
    return render_dashboard(member_message=msg)

def render_dashboard(book_message=None, member_message=None):
    try:
        resp = requests.get(f"{API_BASE}/transactions")
        transactions = resp.json()
    except Exception:
        transactions = []
    return render_template(
        'librarian-dashboard.html',
        transactions=transactions,
        book_message=book_message,
        member_message=member_message
    )

# --- Login Functionality ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            resp = requests.post(f"{API_BASE}/login", json={"email": email, "password": password})
            if resp.status_code == 200:
                user = resp.json()
            else:
                user = None
        except Exception:
            user = None
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['is_librarian'] = bool(user.get('is_librarian', 0))
            session['is_admin'] = bool(user.get('is_admin', 0))
            if session['is_admin']:
                return redirect(url_for('admin_panel'))
            elif session['is_librarian']:
                return redirect(url_for('librarian_dashboard'))
            else:
                return redirect(url_for('book_catalogue'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- Wishlist Feature ---
@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        requests.post(f"{API_BASE}/wishlist/{user_id}", json={"book_id": book_id})
    resp = requests.get(f"{API_BASE}/wishlist/{user_id}")
    wishlist_books = resp.json()
    return render_template('wishlist.html', wishlist=wishlist_books)

@app.route('/add-to-wishlist', methods=['POST'])
def add_to_wishlist():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    book_id = request.form.get('book_id')
    requests.post(f"{API_BASE}/wishlist/{user_id}", json={"book_id": book_id})
    return redirect(url_for('wishlist'))

@app.route('/remove-from-wishlist', methods=['POST'])
def remove_from_wishlist():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    book_id = request.form.get('book_id')
    requests.delete(f"{API_BASE}/wishlist/{user_id}/{book_id}")
    return redirect(url_for('wishlist'))
  
# --- Signup Functionality ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        resp = requests.post(f"{API_BASE}/users", json={
            "name": name,
            "email": email,
            "password": password
        })
        if resp.status_code == 400:
            return render_template('signup.html', error=resp.json().get('error', 'Signup error.'))
        return redirect(url_for('login'))
    return render_template('signup.html')

# --- Admin Panel for User Management ---
@app.route('/admin-panel')
def admin_panel():
    if not session.get('user_id') or not session.get('is_admin'):
        return redirect(url_for('login'))
    resp = requests.get(f"{API_BASE}/users")
    users = resp.json()
    return render_template('admin-panel.html', users=users)

@app.route('/make-librarian/<int:user_id>', methods=['POST'])
def make_librarian(user_id):
    if not session.get('user_id') or not session.get('is_admin'):
        return redirect(url_for('login'))
    requests.post(f"{API_BASE}/users/{user_id}/make-librarian")
    return redirect(url_for('admin_panel'))

@app.route('/remove-librarian/<int:user_id>', methods=['PUT'])
def remove_librarian(user_id):
    if not session.get('user_id') or not session.get('is_admin'):
        return redirect(url_for('login'))
    requests.put(f"{API_BASE}/users/{user_id}/remove-librarian")
    return redirect(url_for('admin_panel'))

@app.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('user_id') or not session.get('is_admin'):
        return redirect(url_for('login'))
    requests.delete(f"{API_BASE}/users/{user_id}")
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
