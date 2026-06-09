from flask import Blueprint, redirect, url_for, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth.oauth import oauth
from app.models.user import User
from app import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({
            "logged_in": True,
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role
        }), 200
    return jsonify({"logged_in": False}), 401

@auth_bp.route('/login/microsoft')
def login_microsoft():
    redirect_uri = url_for('auth.callback', _external=True)
    return oauth.microsoft.authorize_redirect(redirect_uri)

@auth_bp.route('/callback')
def callback():
    try:
        token = oauth.microsoft.authorize_access_token()
        user_info = token.get('userinfo')
        
        email = user_info.get('email') or user_info.get('preferred_username')
        full_name = user_info.get('name')
        external_id = user_info.get('oid') or user_info.get('sub')
        user = User.query.filter_by(external_id=external_id).first()
        if not user:
            domain = email.split('@')[-1].lower()
            
            if domain in ['student.ans-elblag.pl', 'student.uczelnia.pl']:
                role = 'student'
            elif domain in ['ans-elblag.pl', 'uczelnia.pl']:
                role = 'konto_do_zatwierdzenia'
            else:
                return "Brak dostępu: Twój adres email nie należy do domeny uczelnianej.", 403

            user = User(
                email=email,
                full_name=full_name,
                auth_provider='microsoft',
                external_id=external_id,
                role=role
            )
            db.session.add(user)
            db.session.commit()

        if user.role == 'konto_do_zatwierdzenia':
            return "Twoje konto oczekuje na zatwierdzenie przez koordynatora lub administratora.", 403

        login_user(user)
        return redirect('http://localhost:5000/')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Użytkownik o tym adresie email już istnieje."}), 400

    nowy_user = User(
        email=data['email'],
        full_name=data['full_name'],
        external_id=data.get('numer_indeksu'),
        auth_provider='local',
        role='student',
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(nowy_user)
    db.session.commit()
    return jsonify({"message": "Konto lokalne utworzone pomyślnie!"}), 201

@auth_bp.route('/login/local', methods=['POST'])
def login_local():
    data = request.get_json()
    user = User.query.filter_by(email=data['email'], auth_provider='local').first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        login_user(user)
        return jsonify({
            "message": "Zalogowano pomyślnie",
            "user": {"full_name": user.full_name, "role": user.role}
        }), 200
        
    return jsonify({"error": "Nieprawidłowy adres email lub hasło."}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('http://localhost:5000/')