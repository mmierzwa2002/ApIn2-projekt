from flask import Blueprint, request, jsonify, redirect, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.student import Student
from app.models.internship import Internship
from app.models.diary import DziennikPraktyki, WpisDziennika

journal_bp = Blueprint('journal', __name__, url_prefix='/api/journal')


@journal_bp.route('', methods=['GET'])
@login_required
def get_journal():
    internship_id = request.args.get('internship_id', type=int)
    if internship_id:
        dziennik = DziennikPraktyki.query.filter_by(id_formularza=internship_id).first()
        wpisy = dziennik.wpisy if dziennik else []
    else:
        wpisy = WpisDziennika.query.all()
    return jsonify([{
        "id": w.id_wpisu,
        "id_formularza": w.dziennik.id_formularza,
        "nr_dnia": w.nr_dnia,
        "data": w.data_wpisu.strftime('%Y-%m-%d'),
        "godziny": None,
        "opis": w.opis_wykonanych_prac
    } for w in wpisy]), 200


@journal_bp.route('/add', methods=['POST'])
@login_required
def create_journal_entry():
    if current_user.role != 'student':
        flash('Tylko studenci mogą dodawać wpisy do dziennika.', 'danger')
        return redirect('/auth/dashboard')

    praktyka_id = request.form.get('praktyka_id', type=int)
    data_str = request.form.get('data')
    godziny_str = request.form.get('godziny')
    opis = request.form.get('opis', '').strip()

    if not all([praktyka_id, data_str, godziny_str, opis]):
        flash('Wszystkie pola są obowiązkowe.', 'danger')
        return redirect('/auth/dashboard')

    internship = Internship.query.get_or_404(praktyka_id)

    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student or internship.id_studenta != student.id_studenta:
        flash('Brak autoryzacji do tego dziennika.', 'danger')
        return redirect('/auth/dashboard')

    if internship.faza_procesu != 2:
        flash('Dziennik jest zablokowany poza Fazą 2 (Realizacja).', 'danger')
        return redirect('/auth/dashboard')

    try:
        entry_date = datetime.strptime(data_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Nieprawidłowy format daty.', 'danger')
        return redirect('/auth/dashboard')

    try:
        hours = int(godziny_str)
        if hours < 1 or hours > 8:
            raise ValueError
    except ValueError:
        flash('Liczba godzin musi być w przedziale 1–8.', 'danger')
        return redirect('/auth/dashboard')

    if len(opis) < 10:
        flash('Opis musi mieć minimum 10 znaków.', 'danger')
        return redirect('/auth/dashboard')

    # Pobierz lub utwórz dziennik dla tej praktyki
    dziennik = DziennikPraktyki.query.filter_by(id_formularza=praktyka_id).first()
    if not dziennik:
        dziennik = DziennikPraktyki(id_formularza=praktyka_id, status='Active')
        db.session.add(dziennik)
        db.session.flush()

    # Numer dnia = liczba istniejących wpisów + 1
    nr_dnia = len(dziennik.wpisy) + 1
    if nr_dnia > 120:
        flash('Dziennik jest już pełny (120 dni).', 'danger')
        return redirect('/auth/dashboard')

    wpis = WpisDziennika(
        id_dziennika=dziennik.id_dziennika,
        nr_dnia=nr_dnia,
        data_wpisu=entry_date,
        opis_wykonanych_prac=opis,
    )
    db.session.add(wpis)

    # Automatyczne zatwierdzenie po 120 wpisach
    if nr_dnia == 120:
        internship.dziennik_zatwierdzony = True
        internship.liczba_dni_roboczych = 120
        dziennik.status = 'Completed'
        internship.check_and_advance_phase()

    db.session.commit()
    flash(f'Wpis #{nr_dnia} zapisany pomyślnie!', 'success')
    return redirect('/auth/dashboard')


@journal_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_journal_entry(id):
    wpis = WpisDziennika.query.get_or_404(id)
    db.session.delete(wpis)
    db.session.commit()
    return jsonify({"message": "Wpis usunięty"}), 200
