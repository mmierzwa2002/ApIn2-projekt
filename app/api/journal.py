from flask import Blueprint, request, jsonify, redirect, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from app.models.student import Student
from app.models.internship import Internship
from app.models.diary import DziennikPraktyki, WpisDziennika

journal_bp = Blueprint('journal', __name__, url_prefix='/api/journal')

WYMAGANE_DNI = 120
MIN_OPIS = 10
VALID_EFEKTY = {f'{i:02d}' for i in range(1, 14)}  # 01..13


def _get_or_create_dziennik(praktyka_id):
    dziennik = DziennikPraktyki.query.filter_by(id_formularza=praktyka_id).first()
    if not dziennik:
        dziennik = DziennikPraktyki(id_formularza=praktyka_id, status='Active')
        db.session.add(dziennik)
        db.session.flush()
    return dziennik


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
        "nr_efektow": w.nr_efektow,
        "opis": w.opis_wykonanych_prac
    } for w in wpisy]), 200


@journal_bp.route('/add', methods=['POST'])
@login_required
def create_journal_entry():
    praktyka_id = request.form.get('praktyka_id', type=int)
    back = f'/auth/formularze/{praktyka_id}/zal6'

    if current_user.role != 'student':
        flash('Tylko studenci mogą dodawać wpisy do dziennika.', 'danger')
        return redirect(back)

    internship = Internship.query.get_or_404(praktyka_id)

    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student or internship.id_studenta != student.id_studenta:
        flash('Brak autoryzacji do tego dziennika.', 'danger')
        return redirect('/auth/dashboard')

    if internship.faza_procesu != 2:
        flash('Dziennik jest dostępny tylko w Fazie 2 (Realizacja).', 'danger')
        return redirect(back)

    data_str = request.form.get('data', '')
    opis = request.form.get('opis', '').strip()
    efekty = [e.strip() for e in request.form.getlist('efekty') if e.strip()]

    # --- Walidacja daty ---
    try:
        entry_date = datetime.strptime(data_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Nieprawidłowy format daty.', 'danger')
        return redirect(back)

    if entry_date < internship.data_od or entry_date > internship.data_do:
        flash(f'Data musi mieścić się w okresie praktyki '
              f'({internship.data_od.strftime("%d.%m.%Y")} – {internship.data_do.strftime("%d.%m.%Y")}).', 'danger')
        return redirect(back)

    if entry_date.weekday() >= 5:
        flash('Wpis można dodać tylko dla dnia roboczego (poniedziałek–piątek).', 'danger')
        return redirect(back)

    dziennik = _get_or_create_dziennik(praktyka_id)
    wpisy = sorted(dziennik.wpisy, key=lambda w: w.nr_dnia)

    if wpisy and entry_date <= wpisy[-1].data_wpisu:
        flash(f'Data musi być późniejsza niż ostatni wpis '
              f'({wpisy[-1].data_wpisu.strftime("%d.%m.%Y")}).', 'danger')
        return redirect(back)

    # --- Walidacja opisu i efektów ---
    if len(opis) < MIN_OPIS:
        flash(f'Opis prac musi mieć minimum {MIN_OPIS} znaków.', 'danger')
        return redirect(back)

    if not efekty:
        flash('Zaznacz co najmniej jeden efekt uczenia się, którego dotyczą prace.', 'danger')
        return redirect(back)
    if any(e not in VALID_EFEKTY for e in efekty):
        flash('Nieprawidłowy numer efektu uczenia się.', 'danger')
        return redirect(back)

    nr_dnia = len(wpisy) + 1
    if nr_dnia > WYMAGANE_DNI:
        flash(f'Dziennik jest już pełny ({WYMAGANE_DNI} dni).', 'danger')
        return redirect(back)

    db.session.add(WpisDziennika(
        id_dziennika=dziennik.id_dziennika,
        nr_dnia=nr_dnia,
        data_wpisu=entry_date,
        opis_wykonanych_prac=opis,
        nr_efektow=', '.join(efekty),
    ))
    db.session.commit()

    if nr_dnia >= WYMAGANE_DNI:
        flash(f'Wpis #{WYMAGANE_DNI} zapisany. Dziennik kompletny ({WYMAGANE_DNI}/{WYMAGANE_DNI}) '
              '— oczekuje na zatwierdzenie przez ZOPZ.', 'success')
    else:
        flash(f'Wpis #{nr_dnia} zapisany pomyślnie! ({nr_dnia}/{WYMAGANE_DNI} dni)', 'success')
    return redirect(back)


@journal_bp.route('/fill_test', methods=['POST'])
@login_required
def fill_test_journal():
    """Pomocnik testowy: uzupełnia dziennik kolejnymi dniami roboczymi do 120."""
    praktyka_id = request.form.get('praktyka_id', type=int)
    back = f'/auth/formularze/{praktyka_id}/zal6'
    internship = Internship.query.get_or_404(praktyka_id)

    if current_user.role == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student or internship.id_studenta != student.id_studenta:
            flash('Brak autoryzacji do tego dziennika.', 'danger')
            return redirect('/auth/dashboard')
    if internship.faza_procesu != 2:
        flash('Dziennik jest dostępny tylko w Fazie 2 (Realizacja).', 'danger')
        return redirect(back)

    dziennik = _get_or_create_dziennik(praktyka_id)
    wpisy = sorted(dziennik.wpisy, key=lambda w: w.nr_dnia)
    nr_dnia = len(wpisy)
    d = (wpisy[-1].data_wpisu + timedelta(days=1)) if wpisy else internship.data_od

    added = 0
    while nr_dnia < WYMAGANE_DNI and d <= internship.data_do:
        if d.weekday() < 5:
            nr_dnia += 1
            # rotacja efektów 01..13, aby wszystkie 13 zostało pokryte w dzienniku
            kod_efektu = f'{((nr_dnia - 1) % 13) + 1:02d}'
            db.session.add(WpisDziennika(
                id_dziennika=dziennik.id_dziennika,
                nr_dnia=nr_dnia,
                data_wpisu=d,
                opis_wykonanych_prac=f'Dzień {nr_dnia}: realizacja zadań zgodnie z harmonogramem praktyki.',
                nr_efektow=kod_efektu,
            ))
            added += 1
        d += timedelta(days=1)
    db.session.commit()
    flash(f'[TEST] Dodano {added} wpisów. Dziennik: {nr_dnia}/{WYMAGANE_DNI} dni.', 'success')
    return redirect(back)


@journal_bp.route('/undo_last', methods=['POST'])
@login_required
def undo_last_entry():
    """Cofa ostatni wpis dziennika (np. by poprawić pokrycie efektów)."""
    praktyka_id = request.form.get('praktyka_id', type=int)
    back = f'/auth/formularze/{praktyka_id}/zal6'
    internship = Internship.query.get_or_404(praktyka_id)

    if current_user.role == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student or internship.id_studenta != student.id_studenta:
            flash('Brak autoryzacji do tego dziennika.', 'danger')
            return redirect('/auth/dashboard')
    if internship.faza_procesu != 2 or internship.dziennik_zatwierdzony:
        flash('Nie można edytować zatwierdzonego dziennika.', 'danger')
        return redirect(back)

    dziennik = DziennikPraktyki.query.filter_by(id_formularza=praktyka_id).first()
    wpisy = sorted(dziennik.wpisy, key=lambda w: w.nr_dnia) if dziennik else []
    if not wpisy:
        flash('Dziennik jest pusty — nie ma czego cofać.', 'danger')
        return redirect(back)

    ostatni = wpisy[-1]
    nr = ostatni.nr_dnia
    db.session.delete(ostatni)
    db.session.commit()
    flash(f'Cofnięto wpis #{nr}. Możesz dodać go ponownie z właściwymi efektami.', 'success')
    return redirect(back)


@journal_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_journal_entry(id):
    wpis = WpisDziennika.query.get_or_404(id)
    db.session.delete(wpis)
    db.session.commit()
    return jsonify({"message": "Wpis usunięty"}), 200
