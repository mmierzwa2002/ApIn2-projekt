from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Inicjalizacja rozszerzeń
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    load_dotenv()
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///praktyki.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    from app.auth.oauth import oauth
    oauth.init_app(app)
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app