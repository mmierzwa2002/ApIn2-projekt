from flask import Blueprint, redirect, url_for, session, abort, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth.oauth import oauth
from app.models.user import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login/<provider>')
def login(provider):
    if provider == 'microsoft':
        redirect_uri = url_for('auth.callback', provider='microsoft', _external=True)
        return oauth.microsoft.authorize_redirect(redirect_uri)
    elif provider == 'google':
        redirect_uri = url_for('auth.callback', provider='google', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)
    return abort(404)

@auth_bp.route('/callback')
def callback():
    provider = request.args.get('provider', 'microsoft')
    
    if provider == 'microsoft':
        token = oauth.microsoft.authorize_access_token()
        user_info = token.get('userinfo')
        email = user_info.get('email') or user_info.get('preferred_username')
        full_name = user_info.get('name')
        external_id = user_info.get('oid') or user_info.get('sub')
    elif provider == 'google':
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        email = user_info.get('email')
        full_name = user_info.get('name')
        external_id = user_info.get('sub')
    else:
        abort(400)

    user = User.query.filter_by(external_id=external_id).first()
    
    if not user:
        domain = email.split('@')[-1]
        
        # Logika ról na podstawie domeny
        if domain in ['student.ans-elblag.pl', 'student.uczelnia.pl', 'gmail.com']:
            role = 'student'
        elif domain in ['ans-elblag.pl', 'uczelnia.pl']:
            role = 'do_zatwierdzenia'
        else:
            return "Brak dostępu: Nierozpoznana domena", 403

        user = User(
            email=email,
            full_name=full_name,
            auth_provider=provider,
            external_id=external_id,
            role=role
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect('http://127.0.0.1:5500/index.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('http://127.0.0.1:5500/index.html')