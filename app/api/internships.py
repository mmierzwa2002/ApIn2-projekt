from flask import Blueprint, request, jsonify, redirect, flash
from flask_login import login_required, current_user
from app.auth.decorators import role_required
from app.models.student import Student
from app.models.outcome import EfektKsztalcenia, EfektFormularza
from app.models.schedule import HarmonogramPraktyki
from datetime import datetime
from app import db
from app.models.company import Firma
from app.models.internship import Internship

internships_bp = Blueprint('internships', __name__, url_prefix='/api/internships')


@internships_bp.route('', methods=['GET'])
@login_required
def get_internships():
    if current_user.role == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        internships = Internship.query.filter_by(id_studenta=student.id_studenta).all() if student else []
    else:
        internships = Internship.query.all()

    return jsonify([{
        "id": i.id_formularza,
        "id_studenta": i.id_studenta,
        "nazwa_firmy": i.firma.nazwa,
        "data_od": i.data_od.strftime('%Y-%m-%d'),
        "data_do": i.data_do.strftime('%Y-%m-%d'),
        "faza": i.faza_procesu,
        "status": i.status,
        "podpisy": {
            "zal1_zopz": i.zal1_zopz,
            "zal1_dyrektor": i.zal1_dyrektor,
            "zal2a_zopz": i.zal2a_zopz,
            "zal2a_student": i.zal2a_student,
            "zal2a_uopz": i.zal2a_uopz,
            "zal31_dyrektor": i.zal31_dyrektor,
            "zal32_zopz": i.zal32_zopz,
            "dziennik_zatwierdzony": i.dziennik_zatwierdzony,
            "zal4_zopz": i.zal4_zopz,
            "zal4_uopz": i.zal4_uopz,
            "zal7_student": i.zal7_student,
            "zal8_dyrektor": i.zal8_dyrektor,
        }
    } for i in internships]), 200


@internships_bp.route('', methods=['POST'])
@login_required
@role_required('administrator', 'uopz', 'dyrektor')
def create_internship():
    is_form = bool(request.form)
    data = request.get_json(silent=True) or request.form

    def _err(msg, code=400):
        if is_form:
            flash(msg, 'danger')
            return redirect('/auth/dashboard'), None
        return None, (jsonify({'error': msg}), code)

    try:
        id_firmy = int(data.get('id_firmy') or 0)
        id_studenta = int(data.get('id_studenta') or 0)
    except (TypeError, ValueError):
        r, j = _err('Nieprawidłowe ID firmy lub studenta.')
        return r if r else j

    firma = Firma.query.get(id_firmy)
    student = Student.query.get(id_studenta)
    if not firma or not student:
        r, j = _err('Nie znaleziono studenta lub firmy.')
        return r if r else j

    try:
        data_od = datetime.strptime(data.get('data_od', ''), '%Y-%m-%d').date()
        data_do = datetime.strptime(data.get('data_do', ''), '%Y-%m-%d').date()
    except ValueError:
        r, j = _err('Nieprawidłowy format daty (wymagany RRRR-MM-DD).')
        return r if r else j

    if data_od > data_do:
        r, j = _err('Data rozpoczęcia nie może być późniejsza niż zakończenia.')
        return r if r else j

    new_internship = Internship(
        id_studenta=student.id_studenta,
        id_firmy=firma.id_firmy,
        data_od=data_od,
        data_do=data_do,
        faza_procesu=1,
        status='roboczy',
    )
    db.session.add(new_internship)
    db.session.commit()

    if is_form:
        flash(f'Praktyka dla {student.full_name} zarejestrowana (ID: {new_internship.id_formularza}).', 'success')
        return redirect('/auth/dashboard')

    return jsonify({"message": "Formularz praktyki utworzony", "id": new_internship.id_formularza}), 201


@internships_bp.route('/<int:id>', methods=['DELETE'])
@login_required
@role_required('administrator')
def delete_internship(id):
    internship = Internship.query.get_or_404(id)
    db.session.delete(internship)
    db.session.commit()
    return jsonify({"message": "Formularz usunięty"}), 200


@internships_bp.route('/<int:id>/sign', methods=['POST'])
@login_required
def sign_document(id):
    internship = Internship.query.get_or_404(id)
    data = request.get_json(silent=True) or request.form
    document_type = data.get('dokument')
    role = current_user.role

    if internship.faza_procesu == 1:
        if document_type == 'ZAL1' and role == 'zopz':
            internship.zal1_zopz = True
        elif document_type == 'ZAL1' and role == 'dyrektor':
            internship.zal1_dyrektor = True
        elif document_type == 'ZAL2A' and role == 'zopz':
            internship.zal2a_zopz = True
        elif document_type == 'ZAL2A' and role == 'student':
            if not internship.zal2a_zopz:
                return jsonify({"error": "ZOPZ musi najpierw podpisać harmonogram."}), 403
            internship.zal2a_student = True
        elif document_type == 'ZAL2A' and role == 'uopz':
            if not internship.zal2a_student:
                return jsonify({"error": "Student nie podpisał jeszcze Zał. 2a."}), 403
            internship.zal2a_uopz = True
        elif document_type == 'ZAL3_1' and role == 'dyrektor':
            internship.zal31_dyrektor = True
        else:
            return jsonify({"error": "Brak uprawnień lub nieznany dokument w Fazie 1."}), 403

    elif internship.faza_procesu == 2:
        if document_type == 'ZAL3_2' and role == 'zopz':
            internship.zal32_zopz = True
        elif document_type == 'DZIENNIK_GOTOWY' and role == 'zopz':
            internship.dziennik_zatwierdzony = True
        else:
            return jsonify({"error": "Brak uprawnień w Fazie 2."}), 403

    elif internship.faza_procesu == 3:
        if document_type == 'ZAL7' and role == 'student':
            internship.zal7_student = True
        elif document_type == 'ZAL4' and role == 'zopz':
            internship.zal4_zopz = True
        elif document_type == 'ZAL4' and role == 'uopz':
            internship.zal4_uopz = True
        else:
            return jsonify({"error": "Brak uprawnień w Fazie 3."}), 403

    elif internship.faza_procesu == 4:
        if document_type == 'ZAL8' and role == 'dyrektor':
            internship.zal8_dyrektor = True
        else:
            return jsonify({"error": "Tylko Dyrektor może wystawić protokół końcowy."}), 403

    elif internship.faza_procesu == 5:
        return jsonify({"error": "Praktyka jest już zamknięta."}), 400

    internship.check_and_advance_phase()
    db.session.commit()

    redirect_to = data.get('redirect_to')
    if redirect_to:
        flash('Dokument podpisany pomyślnie.', 'success')
        return redirect(redirect_to)

    return jsonify({"message": "Podpisano.", "faza": internship.faza_procesu}), 200


@internships_bp.route('/<int:id>/meta', methods=['POST'])
@login_required
@role_required('administrator', 'uopz')
def update_internship_meta(id):
    internship = Internship.query.get_or_404(id)
    data = request.form

    nr = data.get('nr_porozumienia', '').strip()
    if nr:
        internship.nr_porozumienia = nr

    data_str = data.get('data_porozumienia', '').strip()
    if data_str:
        try:
            internship.data_porozumienia = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Nieprawidłowy format daty porozumienia.', 'danger')

    przedstawiciel = data.get('przedstawiciel_firmy', '').strip()
    if przedstawiciel:
        internship.firma.przedstawiciel = przedstawiciel

    db.session.commit()
    flash('Dane Porozumienia zostały zapisane.', 'success')
    return redirect(data.get('redirect_to') or '/auth/dashboard')


@internships_bp.route('/<int:id>/zal2a', methods=['POST'])
@login_required
@role_required('zopz', 'administrator')
def submit_zal2a(id):
    internship = Internship.query.get_or_404(id)
    if not internship.zal1_zopz or not internship.zal1_dyrektor:
        flash('Zał. 2a można wypełnić dopiero po podpisaniu Zał. 1 przez obie strony.', 'danger')
        return redirect(f'/auth/formularze/{id}/zal2a')
    if internship.faza_procesu != 1 or internship.zal2a_zopz:
        flash('Formularz został już podpisany lub praktyka jest w innej fazie.', 'danger')
        return redirect(f'/auth/formularze/{id}/zal2a')

    data = request.form

    # Walidacja i zapis efektów kształcenia
    for i in range(1, 14):
        kod = f'{i:02d}'
        opis_prac = data.get(f'efekt_{kod}', '').strip()
        if not opis_prac:
            flash(f'Efekt {kod}: opis prac jest wymagany.', 'danger')
            return redirect(f'/auth/formularze/{id}/zal2a')
        efekt_k = EfektKsztalcenia.query.filter_by(kod=kod).first()
        if not efekt_k:
            continue
        existing = EfektFormularza.query.filter_by(
            id_formularza=id, id_efektu=efekt_k.id_efektu).first()
        if existing:
            existing.opis_prac = opis_prac
        else:
            db.session.add(EfektFormularza(
                id_formularza=id, id_efektu=efekt_k.id_efektu, opis_prac=opis_prac))

    # Zapis harmonogramu (najpierw usuń stare)
    HarmonogramPraktyki.query.filter_by(id_formularza=id).delete()
    total_dni = 0
    lp = 0
    for i in range(1, 14):
        dzial = data.get(f'dzial_{i:02d}', '').strip()
        dni_str = data.get(f'dni_{i:02d}', '').strip()
        if not dzial and not dni_str:
            continue
        if not dzial or not dni_str:
            flash(f'Harmonogram pozycja {i}: wypełnij i nazwę działu, i liczbę dni.', 'danger')
            db.session.rollback()
            return redirect(f'/auth/formularze/{id}/zal2a')
        try:
            dni = int(dni_str)
            if dni <= 0:
                raise ValueError()
        except ValueError:
            flash(f'Harmonogram pozycja {i}: nieprawidłowa liczba dni.', 'danger')
            db.session.rollback()
            return redirect(f'/auth/formularze/{id}/zal2a')
        lp += 1
        total_dni += dni
        db.session.add(HarmonogramPraktyki(
            id_formularza=id, lp=lp,
            dzial_komorka=dzial, planowana_liczba_dni=dni))

    if total_dni != 120:
        flash(f'Suma dni harmonogramu musi wynosić 120 (aktualnie: {total_dni}).', 'danger')
        db.session.rollback()
        return redirect(f'/auth/formularze/{id}/zal2a')

    internship.zal2a_zopz = True
    db.session.commit()
    flash('Zał. 2a wypełniony i podpisany przez ZOPZ.', 'success')
    return redirect(f'/auth/formularze/{id}/zal2a')


@internships_bp.route('/<int:id>/zal2a/reject', methods=['POST'])
@login_required
@role_required('uopz', 'administrator')
def reject_zal2a(id):
    internship = Internship.query.get_or_404(id)
    internship.zal2a_zopz = False
    internship.zal2a_student = False
    db.session.commit()
    flash('Zał. 2a odrzucony — ZOPZ musi go ponownie podpisać.', 'warning')
    return redirect(f'/auth/formularze/{id}/zal2a')
