import re
from flask import Blueprint, render_template, redirect, request, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth.oauth import oauth
from app.models.user import User
from app.models.student import Student
from app.models.internship import Internship
from app import db


def _make_student_record(user):
    """Tworzy rekord studenta z danych konta (bez zapisu do sesji)."""
    clean_name = re.sub(r'\s*\(\d+\)\s*$', '', user.full_name or '').strip()
    parts = clean_name.split(' ', 1)
    imie = parts[0] if parts else user.email.split('@')[0]
    nazwisko = parts[1] if len(parts) > 1 else ''
    nr_albumu = user.email.split('@')[0]
    if Student.query.filter_by(nr_albumu=nr_albumu).first():
        return None
    return Student(user_id=user.id, imie=imie, nazwisko=nazwisko,
                   nr_albumu=nr_albumu, kierunek='Nieznany')

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/auth/dashboard')
    return render_template('login.html')


@auth_bp.route('/login/local', methods=['POST'])
def login_local():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email, auth_provider='local').first()
    if user and check_password_hash(user.password_hash, password):
        if user.role == 'konto_do_zatwierdzenia':
            return redirect('/auth/pending')
        login_user(user)
        return redirect('/auth/dashboard')
    flash('Nieprawidłowy adres e-mail lub hasło.', 'danger')
    return redirect('/auth/login')


@auth_bp.route('/register', methods=['POST'])
def register():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    password = request.form.get('password')
    if User.query.filter_by(email=email).first():
        flash('Użytkownik o tym adresie e-mail już istnieje.', 'danger')
        return redirect('/auth/login')
    nowy_user = User(
        email=email,
        full_name=full_name,
        auth_provider='local',
        role='student',
        password_hash=generate_password_hash(password)
    )
    db.session.add(nowy_user)
    db.session.commit()
    flash('Konto studenckie utworzone. Możesz się zalogować.', 'success')
    return redirect('/auth/login')


@auth_bp.route('/login/microsoft')
def login_microsoft():
    redirect_uri = request.host_url.rstrip('/') + '/auth/callback'
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
            # indeks@student.ans-elblag.pl → student, wszystko inne → oczekuje na zatwierdzenie
            domain = email.split('@')[-1].lower()
            role = 'student' if domain == 'student.ans-elblag.pl' else 'konto_do_zatwierdzenia'
            user = User(
                email=email,
                full_name=full_name,
                auth_provider='microsoft',
                external_id=external_id,
                role=role
            )
            db.session.add(user)
            db.session.flush()

            if role == 'student':
                student = _make_student_record(user)
                if student:
                    db.session.add(student)

            db.session.commit()

        if user.role == 'konto_do_zatwierdzenia':
            return redirect('/auth/pending')

        # Napraw brakujący rekord studenta (np. konto założone przed tą logiką)
        if user.role == 'student' and not Student.query.filter_by(user_id=user.id).first():
            student = _make_student_record(user)
            if student:
                db.session.add(student)
                db.session.commit()

        login_user(user)
        return redirect('/auth/dashboard')

    except Exception as e:
        return f"Błąd uwierzytelniania OAuth2: {str(e)}", 500


@auth_bp.route('/pending')
def pending():
    return render_template('pending.html')


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    from app.models.company import Firma

    if current_user.role == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        internships = Internship.query.filter_by(id_studenta=student.id_studenta).all() if student else []
    else:
        internships = Internship.query.all()

    pending_users = []
    if current_user.role == 'administrator':
        pending_users = User.query.filter_by(role='konto_do_zatwierdzenia').all()

    firms = []
    students = []
    if current_user.role in ('uopz', 'administrator'):
        firms = Firma.query.order_by(Firma.nazwa).all()
        students = Student.query.order_by(Student.nazwisko, Student.imie).all()

    return render_template('dashboard.html', internships=internships, pending_users=pending_users,
                           firms=firms, students=students)


@auth_bp.route('/admin/approvals')
@login_required
def admin_approvals():
    if current_user.role != 'administrator':
        flash('Brak uprawnień.', 'danger')
        return redirect('/auth/dashboard')
    pending_users = User.query.filter_by(role='konto_do_zatwierdzenia').all()
    return render_template('admin_approvals.html', pending_users=pending_users)


@auth_bp.route('/admin/approve/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    if current_user.role != 'administrator':
        flash('Brak uprawnień.', 'danger')
        return redirect('/auth/dashboard')
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role not in ['uopz', 'zopz', 'dyrektor']:
        flash('Nieprawidłowa rola.', 'danger')
        return redirect('/auth/admin/approvals')
    user.role = new_role
    db.session.commit()
    flash(f'Konto {user.full_name} ({user.email}) zatwierdzone jako {new_role}.', 'success')
    return redirect('/auth/admin/approvals')


@auth_bp.route('/admin/internship/<int:id>/delete', methods=['POST'])
@login_required
def delete_internship(id):
    if current_user.role != 'administrator':
        flash('Brak uprawnień.', 'danger')
        return redirect('/auth/dashboard')
    from app.models.internship import Internship
    from app.models.outcome import EfektFormularza
    from app.models.schedule import HarmonogramPraktyki
    internship = Internship.query.get_or_404(id)
    EfektFormularza.query.filter_by(id_formularza=id).delete()
    HarmonogramPraktyki.query.filter_by(id_formularza=id).delete()
    db.session.delete(internship)
    db.session.commit()
    flash(f'Praktyka #{id} została usunięta.', 'success')
    return redirect('/auth/dashboard')


@auth_bp.route('/formularze/<int:id>/zal2a')
@login_required
def view_zal2a(id):
    from app.models.outcome import EfektKsztalcenia, EfektFormularza
    from app.models.schedule import HarmonogramPraktyki
    internship = Internship.query.get_or_404(id)
    if current_user.role == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student or internship.id_studenta != student.id_studenta:
            abort(403)
    all_efekty = EfektKsztalcenia.query.order_by(EfektKsztalcenia.id_efektu).all()
    efekty_map = {ef.id_efektu: ef.opis_prac
                  for ef in EfektFormularza.query.filter_by(id_formularza=id).all()}
    harmonogram = HarmonogramPraktyki.query.filter_by(
        id_formularza=id).order_by(HarmonogramPraktyki.lp).all()
    return render_template('formularze/zal2a.html', p=internship,
                           all_efekty=all_efekty, efekty_map=efekty_map,
                           harmonogram=harmonogram)


@auth_bp.route('/formularze/<int:id>/zal1')
@login_required
def view_zal1(id):
    internship = Internship.query.get_or_404(id)
    if current_user.role == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student or internship.id_studenta != student.id_studenta:
            abort(403)
    return render_template('formularze/zal1.html', p=internship)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/auth/login')
