from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flasgger import Swagger
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    load_dotenv()
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///praktyki.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.config['SWAGGER'] = {
    'title': 'API Systemu Praktyk',
    'uiversion': 3,
    'openapi': '3.0.0'
    }
    Swagger(app, template_file='../swagger.yaml')
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    from app.auth.oauth import oauth
    oauth.init_app(app)
    from app.models.user import User
    from app.models.internship import Internship
    from app.models.document import Document    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from app.api.errors import errors_bp
    from app.api.students import students_bp
    from app.api.internships import internships_bp
    from app.api.documents import documents_bp

    app.register_blueprint(errors_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(internships_bp)
    app.register_blueprint(documents_bp)

    return app