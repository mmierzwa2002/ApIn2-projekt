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

    app = Flask(__name__, static_folder='../static', static_url_path='', template_folder='../templates')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'pancerne-haslo-sesji-praktyk-999!')

    database_url = os.getenv('DATABASE_URL', 'sqlite:///praktyki.db')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    CORS(app, supports_credentials=True)

    app.config['SWAGGER'] = {'title': 'API Systemu Praktyk', 'uiversion': 3, 'openapi': '3.0.0'}
    Swagger(app, template_file='../swagger.yaml')

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": "Brak dostępu. Zaloguj się do systemu."}), 401

    from app.auth.oauth import oauth
    oauth.init_app(app)

    # Importy modeli — kolejność ma znaczenie (zależności FK)
    from app.models.user import User
    from app.models.company import Firma
    from app.models.student import Student
    from app.models.supervisor import Opiekun
    from app.models.internship import Internship
    from app.models.outcome import EfektKsztalcenia, EfektFormularza, PotwierdzenieEfektu
    from app.models.schedule import HarmonogramPraktyki
    from app.models.card import KartaPraktyki
    from app.models.diary import DziennikPraktyki, WpisDziennika
    from app.models.report import Sprawozdanie
    from app.models.survey import Ankieta
    from app.models.protocol import ProtokolZaliczenia
    from app.models.document import Document

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        pending_count = 0
        if current_user.is_authenticated and current_user.role == 'administrator':
            pending_count = User.query.filter_by(role='konto_do_zatwierdzenia').count()

        def staff(role):
            """Imię i nazwisko pierwszej osoby o danej roli (podpis na dokumentach)."""
            u = User.query.filter_by(role=role).order_by(User.id).first()
            return u.full_name if u else ''

        return {'pending_count': pending_count, 'staff': staff}

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.api.errors import errors_bp
    from app.api.students import students_bp
    from app.api.internships import internships_bp
    from app.api.documents import documents_bp
    from app.api.journal import journal_bp
    from app.api.outcomes import outcomes_bp
    from app.api.firms import firms_bp
    from app.api.pdf import pdf_bp

    app.register_blueprint(errors_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(internships_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(outcomes_bp)
    app.register_blueprint(firms_bp)
    app.register_blueprint(pdf_bp)

    return app
