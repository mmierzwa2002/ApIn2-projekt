from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    full_name = db.Column(db.String(255))
    auth_provider = db.Column(db.String(50), default="microsoft")
    external_id = db.Column(db.String(255), unique=True)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    password_hash = db.Column(db.String(255), nullable=True)