import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    # create the app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

    # configure the database to use MySQL only
    # Load variables from .env file if python-dotenv is installed
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
        
    mysql_user = os.environ.get("MYSQL_USER", "root")
    mysql_password = os.environ.get("MYSQL_PASSWORD", "Abcd@123")
    mysql_host = os.environ.get("MYSQL_HOST", "localhost")
    mysql_db = os.environ.get("MYSQL_DB", "library")
    mysql_port = int(os.environ.get("MYSQL_PORT", "3306"))
    
    # MySQL connection string
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
    print(f"Connecting to MySQL database: {mysql_host}:{mysql_port}/{mysql_db}")
    
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # initialize the app with the extensions
    db.init_app(app)
    
    # Configure Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    with app.app_context():
        # Import models for table creation
        import models  # noqa: F401
        
        # Create database tables
        db.create_all()
        
        # Import and register routes
        from routes import register_routes
        register_routes(app)

    return app
