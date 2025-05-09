# Library Management System

A Flask-based Library Management System with book and member management, circulation tracking, and MySQL database integration.

## Features

- Book management (add, edit, delete, search)
- Member management (add, edit, delete, search)
- Book circulation (issue and return books)
- History tracking of all transactions
- Dashboard with statistics and recent activities
- Responsive design using Bootstrap

## Requirements

- Python 3.6+
- MySQL Server
- MySQL Workbench (recommended for database management)

## Setup Instructions

### 1. Database Setup

1. Install MySQL Server and MySQL Workbench
2. Open MySQL Workbench and connect to your local MySQL server
3. Create a new database schema:
   - Run the `library_schema.sql` script in MySQL Workbench, or
   - Execute the following command in the terminal:
     ```
     mysql -u root -p < library_schema.sql
     ```

### 2. Environment Configuration

1. Clone or download this repository
2. Navigate to the project directory
3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Configure environment variables in the `.env` file:
   ```
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_HOST=localhost
   MYSQL_DB=library
   MYSQL_PORT=3306
   SESSION_SECRET=your_secret_key_here
   ```

### 3. Running the Application

1. Start the application:
   ```bash
   flask run
   ```
   or
   ```bash
   python main.py
   ```
2. Access the application in your browser at `http://localhost:5000`

## Database Schema

The application uses the following tables:

1. **Book**
   - id, isbn, title, author, publisher, year, category, quantity, available

2. **Member**
   - id, first_name, last_name, email, phone, address, registration_date, active

3. **BookIssue**
   - id, book_id, member_id, issue_date, return_date, due_date, returned

## Usage

1. **Dashboard** - View system statistics and recent activity
2. **Books** - Manage books (add, edit, delete, search)
3. **Members** - Manage library members (add, edit, delete, search)
4. **Circulation** - Issue and return books
5. **History** - View complete transaction history