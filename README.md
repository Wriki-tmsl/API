# Library Management System Portfolio

## Overview

This project is a web-based Library Management System built with Flask (Python) and MySQL.  
It features user authentication, book catalogue, librarian dashboard, wishlist, and an admin panel for user management.  
All database operations are handled via a dedicated API server.

---

## Features

- **User Login & Signup**
- **Book Catalogue** (browse, add to wishlist)
- **Wishlist** (add/remove books)
- **Librarian Dashboard** (manage books, members, transactions)
- **Admin Panel** (manage users, promote/demote librarians)
- **RESTful API Server** for all database actions

---

## Setup

### 1. Database

Create the required tables and insert mock data:

```sh
mysql -u tranzsilica -p library < setup/create_tables.sql
mysql -u tranzsilica -p library < setup/insert_mock_data.sql
```

### 2. API Server

Start the API server:

```sh
python api_server.py
```

### 3. Flask Web App

Start the main Flask app:

```sh
python app.py
```

---

## Folder Structure

```
src/
  components/      # HTML templates
  styles/          # CSS files
setup/
  create_tables.sql
  insert_mock_data.sql
app.py             # Main Flask app (frontend/routes)
api_server.py      # API server (database actions)
```

---

## Usage

- Visit `http://localhost:5000` for the web app.
- Login as:
  - User: `jane@library.com` / `password123`
  - Librarian: `john@library.com` / `password123`
  - Admin: `admin@library.com` / `adminpass`
- Explore catalogue, wishlist, dashboard, and admin panel as per your role.

---

## Notes

- Change `app.secret_key` in `app.py` for production.
- Update `DB_CONFIG` in `api_server.py` with your MySQL credentials.
- All database actions are performed via REST API calls from `app.py` to `api_server.py`.