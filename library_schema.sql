-- Library Management System Database Schema

-- Create Database if not exists
CREATE DATABASE IF NOT EXISTS library;
USE library;

-- Book Table
CREATE TABLE IF NOT EXISTS book (
    id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(200) NOT NULL,
    publisher VARCHAR(200),
    year INT,
    category VARCHAR(100),
    quantity INT NOT NULL DEFAULT 1,
    available INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Member Table
CREATE TABLE IF NOT EXISTS member (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20),
    address VARCHAR(200),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

-- Book Issue Table
CREATE TABLE IF NOT EXISTS book_issue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    return_date TIMESTAMP NULL,
    due_date TIMESTAMP NOT NULL,
    returned BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (book_id) REFERENCES book(id),
    FOREIGN KEY (member_id) REFERENCES member(id)
);

-- Add sample data for testing (uncomment if needed)
/*
-- Sample Books
INSERT INTO book (isbn, title, author, publisher, year, category, quantity, available) VALUES
('9780132350884', 'Clean Code', 'Robert C. Martin', 'Prentice Hall', 2008, 'Programming', 3, 3),
('9780134757599', 'Practical Software Design', 'David Thomas', 'Addison-Wesley', 2019, 'Software Engineering', 2, 2),
('9780262033848', 'Introduction to Algorithms', 'Thomas H. Cormen', 'MIT Press', 2009, 'Computer Science', 5, 5),
('9781449355739', 'Learning Python', 'Mark Lutz', 'O\'Reilly Media', 2013, 'Programming', 3, 3),
('9781491904244', 'You Don\'t Know JS', 'Kyle Simpson', 'O\'Reilly Media', 2015, 'Programming', 2, 2);

-- Sample Members
INSERT INTO member (first_name, last_name, email, phone, address, active) VALUES
('John', 'Doe', 'john.doe@example.com', '123-456-7890', '123 Main St, Anytown, USA', TRUE),
('Jane', 'Smith', 'jane.smith@example.com', '987-654-3210', '456 Oak Ave, Somecity, USA', TRUE),
('Alice', 'Johnson', 'alice.johnson@example.com', '555-123-4567', '789 Pine Rd, Othertown, USA', TRUE);
*/