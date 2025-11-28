CREATE TABLE members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    is_librarian TINYINT(1) DEFAULT 0,
    is_admin TINYINT(1) DEFAULT 0
);

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    isbn VARCHAR(20) NOT NULL,
    library VARCHAR(100) NOT NULL,
    quantity INT DEFAULT 1
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    date DATE NOT NULL,
    action VARCHAR(20) NOT NULL, -- e.g. 'Borrowed', 'Returned'
    FOREIGN KEY (user_id) REFERENCES members(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

CREATE TABLE wishlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES members(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);