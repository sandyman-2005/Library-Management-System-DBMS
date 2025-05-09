import logging
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, g
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from app import db
from models import Book, Member, BookIssue, User
from forms import BookForm, MemberForm, BookIssueForm, BookReturnForm, SearchForm, LoginForm, RegistrationForm

def register_routes(app):
    # Add before_request handler to set up common template variables
    @app.before_request
    def before_request():
        g.now = datetime.utcnow()
    
    # Add context processor to inject variables into all templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    # Authentication routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                flash('Login successful!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Login failed. Please check your username and password.', 'danger')
        
        return render_template('login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            try:
                user = User(username=form.username.data, email=form.email.data)
                user.set_password(form.password.data)
                
                db.session.add(user)
                db.session.commit()
                
                flash('Your account has been created! You can now log in.', 'success')
                return redirect(url_for('login'))
            except SQLAlchemyError as e:
                db.session.rollback()
                logging.error(f"Error registering user: {str(e)}")
                flash(f"An error occurred: {str(e)}", "danger")
        
        return render_template('register.html', form=form)
    
    @app.route('/logout')
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
    
    # Home route
    @app.route('/')
    @login_required
    def index():
        # Get some statistics for the dashboard
        try:
            total_books = Book.query.count()
            total_members = Member.query.count()
            books_issued = BookIssue.query.filter_by(returned=False).count()
            books_available = sum([book.available for book in Book.query.all()])
            
            # Get recent activities
            recent_issues = BookIssue.query.order_by(BookIssue.issue_date.desc()).limit(5).all()
            recent_returns = BookIssue.query.filter_by(returned=True).order_by(BookIssue.return_date.desc()).limit(5).all()
            
            # Get overdue books
            overdue_issues = BookIssue.query.filter(
                BookIssue.returned == False,
                BookIssue.due_date < datetime.utcnow()
            ).all()
            
            return render_template('index.html', 
                                total_books=total_books,
                                total_members=total_members,
                                books_issued=books_issued,
                                books_available=books_available,
                                recent_issues=recent_issues,
                                recent_returns=recent_returns,
                                overdue_issues=overdue_issues)
        except SQLAlchemyError as e:
            logging.error(f"Database error: {str(e)}")
            flash(f"An error occurred while loading dashboard data: {str(e)}", "danger")
            return render_template('index.html')

    # Book routes
    @app.route('/books')
    @login_required
    def books():
        search_form = SearchForm()
        page = request.args.get('page', 1, type=int)
        query = request.args.get('query', '')
        search_type = request.args.get('type', 'title')
        
        if query:
            # Perform search based on selected type
            if search_type == 'title':
                books = Book.query.filter(Book.title.contains(query)).paginate(page=page, per_page=10)
            elif search_type == 'author':
                books = Book.query.filter(Book.author.contains(query)).paginate(page=page, per_page=10)
            elif search_type == 'isbn':
                books = Book.query.filter(Book.isbn.contains(query)).paginate(page=page, per_page=10)
            elif search_type == 'category':
                books = Book.query.filter(Book.category.contains(query)).paginate(page=page, per_page=10)
        else:
            books = Book.query.order_by(Book.title).paginate(page=page, per_page=10)
        
        return render_template('books.html', books=books, search_form=search_form, query=query, search_type=search_type)

    @app.route('/books/add', methods=['GET', 'POST'])
    def add_book():
        form = BookForm()
        if form.validate_on_submit():
            try:
                # Check if ISBN already exists
                existing_book = Book.query.filter_by(isbn=form.isbn.data).first()
                if existing_book:
                    flash('A book with this ISBN already exists!', 'danger')
                    return render_template('add_book.html', form=form)
                
                book = Book(
                    isbn=form.isbn.data,
                    title=form.title.data,
                    author=form.author.data,
                    publisher=form.publisher.data,
                    year=form.year.data,
                    category=form.category.data,
                    quantity=form.quantity.data,
                    available=form.quantity.data
                )
                db.session.add(book)
                db.session.commit()
                flash('Book added successfully!', 'success')
                return redirect(url_for('books'))
            except SQLAlchemyError as e:
                db.session.rollback()
                logging.error(f"Error adding book: {str(e)}")
                flash(f"An error occurred: {str(e)}", "danger")
        
        return render_template('add_book.html', form=form)

    @app.route('/books/edit/<int:id>', methods=['GET', 'POST'])
    def edit_book(id):
        book = Book.query.get_or_404(id)
        form = BookForm(obj=book)
        
        if form.validate_on_submit():
            try:
                # Calculate difference in quantity to update available count
                quantity_diff = form.quantity.data - book.quantity
                
                # Update book details
                book.isbn = form.isbn.data
                book.title = form.title.data
                book.author = form.author.data
                book.publisher = form.publisher.data
                book.year = form.year.data
                book.category = form.category.data
                book.quantity = form.quantity.data
                
                # Update available count based on quantity change
                book.available += quantity_diff
                
                db.session.commit()
                flash('Book updated successfully!', 'success')
                return redirect(url_for('books'))
            except SQLAlchemyError as e:
                db.session.rollback()
                logging.error(f"Error updating book: {str(e)}")
                flash(f"An error occurred: {str(e)}", "danger")
        
        return render_template('edit_book.html', form=form, book=book)

    @app.route('/books/delete/<int:id>', methods=['POST'])
    def delete_book(id):
        book = Book.query.get_or_404(id)
        
        # Check if the book has any issues that haven't been returned
        active_issues = BookIssue.query.filter_by(book_id=id, returned=False).count()
        if active_issues > 0:
            flash('Cannot delete this book as it has active issues!', 'danger')
            return redirect(url_for('books'))
        
        try:
            db.session.delete(book)
            db.session.commit()
            flash('Book deleted successfully!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Error deleting book: {str(e)}")
            flash(f"An error occurred: {str(e)}", "danger")
        
        return redirect(url_for('books'))

    # Member routes
    @app.route('/members')
    def members():
        search_query = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        
        if search_query:
            members = Member.query.filter(
                (Member.first_name.contains(search_query)) | 
                (Member.last_name.contains(search_query)) | 
                (Member.email.contains(search_query))
            ).paginate(page=page, per_page=10)
        else:
            members = Member.query.order_by(Member.registration_date.desc()).paginate(page=page, per_page=10)
        
        return render_template('members.html', members=members, search_query=search_query)

    @app.route('/members/add', methods=['GET', 'POST'])
    def add_member():
        form = MemberForm()
        if form.validate_on_submit():
            try:
                # Check if email already exists
                existing_member = Member.query.filter_by(email=form.email.data).first()
                if existing_member:
                    flash('A member with this email already exists!', 'danger')
                    return render_template('add_member.html', form=form)
                
                member = Member(
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    address=form.address.data,
                    active=form.active.data
                )
                db.session.add(member)
                db.session.commit()
                flash('Member added successfully!', 'success')
                return redirect(url_for('members'))
            except SQLAlchemyError as e:
                db.session.rollback()
                logging.error(f"Error adding member: {str(e)}")
                flash(f"An error occurred: {str(e)}", "danger")
        
        return render_template('add_member.html', form=form)

    @app.route('/members/edit/<int:id>', methods=['GET', 'POST'])
    def edit_member(id):
        member = Member.query.get_or_404(id)
        form = MemberForm(obj=member)
        
        if form.validate_on_submit():
            try:
                member.first_name = form.first_name.data
                member.last_name = form.last_name.data
                member.email = form.email.data
                member.phone = form.phone.data
                member.address = form.address.data
                member.active = form.active.data
                
                db.session.commit()
                flash('Member updated successfully!', 'success')
                return redirect(url_for('members'))
            except SQLAlchemyError as e:
                db.session.rollback()
                logging.error(f"Error updating member: {str(e)}")
                flash(f"An error occurred: {str(e)}", "danger")
        
        return render_template('edit_member.html', form=form, member=member)

    @app.route('/members/delete/<int:id>', methods=['POST'])
    def delete_member(id):
        member = Member.query.get_or_404(id)
        
        # Check if member has any active issues
        active_issues = BookIssue.query.filter_by(member_id=id, returned=False).count()
        if active_issues > 0:
            flash('Cannot delete member with active book issues!', 'danger')
            return redirect(url_for('members'))
        
        try:
            db.session.delete(member)
            db.session.commit()
            flash('Member deleted successfully!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Error deleting member: {str(e)}")
            flash(f"An error occurred: {str(e)}", "danger")
        
        return redirect(url_for('members'))

    # Circulation routes
    @app.route('/circulation')
    def circulation():
        # Get all active book issues
        active_issues = BookIssue.query.filter_by(returned=False).order_by(BookIssue.issue_date.desc()).all()
        return render_template('circulation.html', active_issues=active_issues)

    @app.route('/circulation/issue', methods=['GET', 'POST'])
    def issue_book():
        form = BookIssueForm()
        
        # Populate select fields with available books and active members
        form.book_id.choices = [(book.id, f"{book.title} by {book.author} (ISBN: {book.isbn})") 
                                for book in Book.query.filter(Book.available > 0).all()]
        form.member_id.choices = [(member.id, f"{member.first_name} {member.last_name} ({member.email})") 
                                for member in Member.query.filter_by(active=True).all()]
        
        if form.validate_on_submit():
            try:
                book = Book.query.get(form.book_id.data)
                member = Member.query.get(form.member_id.data)
                
                if not book or not member:
                    flash('Invalid book or member selection!', 'danger')
                    return redirect(url_for('issue_book'))
                
                if book.available <= 0:
                    flash('This book is not available for issue!', 'danger')
                    return redirect(url_for('issue_book'))
                
                # Create new book issue
                issue = BookIssue(
                    book_id=book.id,
                    member_id=member.id,
                    issue_date=datetime.utcnow(),
                    due_date=form.due_date.data,
                    returned=False
                )
                
                # Update book availability
                book.available -= 1
                
                db.session.add(issue)
                db.session.commit()
                
                flash(f'Book "{book.title}" has been issued to {member.first_name} {member.last_name}!', 'success')
                return redirect(url_for('circulation'))
            except SQLAlchemyError as e:
                db.session.rollback()
                logging.error(f"Error issuing book: {str(e)}")
                flash(f"An error occurred: {str(e)}", "danger")
        
        return render_template('issue_book.html', form=form)

    @app.route('/circulation/return', methods=['GET', 'POST'])
    def return_book():
        form = BookReturnForm()
        
        # Populate select field with active book issues
        active_issues = BookIssue.query.filter_by(returned=False).all()
        form.issue_id.choices = [(issue.id, f"{issue.book.title} - Issued to {issue.member.full_name} on {issue.issue_date.strftime('%Y-%m-%d')}") 
                                for issue in active_issues]
        
        if form.validate_on_submit():
            try:
                issue = BookIssue.query.get(form.issue_id.data)
                
                if not issue:
                    flash('Invalid book issue selection!', 'danger')
                    return redirect(url_for('return_book'))
                
                # Update issue record
                issue.return_date = datetime.utcnow()
                issue.returned = True
                
                # Update book availability
                book = Book.query.get(issue.book_id)
                book.available += 1
                
                db.session.commit()
                
                flash(f'Book "{book.title}" has been returned successfully!', 'success')
                return redirect(url_for('circulation'))
            except SQLAlchemyError as e:
                db.session.rollback()
                logging.error(f"Error returning book: {str(e)}")
                flash(f"An error occurred: {str(e)}", "danger")
        
        return render_template('return_book.html', form=form)

    @app.route('/history')
    def history():
        page = request.args.get('page', 1, type=int)
        
        # Get all book issues with pagination
        issues = BookIssue.query.order_by(BookIssue.issue_date.desc()).paginate(page=page, per_page=10)
        return render_template('history.html', issues=issues)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('layout.html', error=True, error_code=404, error_message="Page Not Found"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('layout.html', error=True, error_code=500, error_message="Internal Server Error"), 500
