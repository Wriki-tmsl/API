-- Insert mock members
INSERT INTO members (name, email, password, is_librarian, is_admin) VALUES
('Jane Smith', 'jane@library.com', 'password123', 0, 0),
('John Doe', 'john@library.com', 'password123', 1, 0),
('Admin User', 'admin@library.com', 'adminpass', 1, 1);

-- Insert mock books
INSERT INTO books (title, author, isbn, library, quantity) VALUES
('1984', 'George Orwell', '9780451524935', 'Central Library', 5),
('Pride and Prejudice', 'Jane Austen', '9780141439518', 'Community Library', 3),
('The Hobbit', 'J.R.R. Tolkien', '9780547928227', 'Central Library', 2);

-- Insert mock transactions
INSERT INTO transactions (user_id, book_id, date, action) VALUES
(1, 1, '2024-08-01', 'Borrowed'),
(1, 2, '2024-08-05', 'Borrowed'),
(2, 3, '2024-07-15', 'Returned');

-- Insert mock wishlists
INSERT INTO wishlists (user_id, book_id) VALUES
(1, 1),
(1, 2),
(2,