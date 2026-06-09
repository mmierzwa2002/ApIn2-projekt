from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flasgger import Swagger
from dotenv import load_dotenv
from flask_cors import CORS
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    load_dotenv()
    
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    
    # Konfiguracja bezpiecznego klucza sesji (naprawia RuntimeError)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'pancerne-haslo-sesji-praktyk-999!')
    
    # Dynamiczna migracja bazy: priorytet ma PostgreSQL z .env, spadek do lokalnego SQLite
    database_url = os.getenv('DATABASE_URL', 'sqlite:///praktyki.db')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    
    # Zaawansowana konfiguracja CORS umożliwiająca autoryzację sesyjną między różnymi portami
    CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5500", "http://localhost:5500"])
    
    app.config['SWAGGER'] = {
        'title': 'API Systemu Praktyk',
        'uiversion': 3,
        'openapi': '3.0.0'
    }
    Swagger(app, template_file='../swagger.yaml')
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Obsługa nieautoryzowanych żądań API dla interfejsu SPA (zwraca czysty JSON 401 zamiast przekierowania)
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": "Brak dostępu. Zaloguj się do systemu."}), 401
    
    from app.auth.oauth import oauth
    oauth.init_app(app)
    
    from app.models.user import User
    from app.models.internship import Internship
    from app.models.document import Document
    from app.models.journal_entry import JournalEntry
    from app.models.learning_outcome import LearningOutcome
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Rejestracja modułów uwierzytelniania i generowania PDF
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    #from app.pdf_generator import pdf_bp
    #app.register_blueprint(pdf_bp)

    # Rejestracja modułów REST API
    from app.api.errors import errors_bp
    from app.api.students import students_bp
    from app.api.internships import internships_bp
    from app.api.documents import documents_bp
    from app.api.journal import journal_bp
    from app.api.outcomes import outcomes_bp

    app.register_blueprint(errors_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(internships_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(outcomes_bp)

    return app