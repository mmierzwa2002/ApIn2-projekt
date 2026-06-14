from flask import Blueprint, request, jsonify, redirect, flash
from flask_login import login_required, current_user
from app.auth.decorators import role_required
from app.models.student import Student
from app.models.outcome import EfektKsztalcenia, EfektFormularza
from app.models.schedule import HarmonogramPraktyki
from datetime import datetime, timedelta
from app import db
from app.models.company import Firma
from app.models.internship import Internship
from app.models.report import Sprawozdanie
from app.models.card import KartaPraktyki

internships_bp = Blueprint('internships', __name__, url_prefix='/api/internships')

WYMAGANE_DNI_ROBOCZE = 120
WSZYSTKIE_EFEKTY = {f'{i:02d}' for i in range(1, 14)}  # 01..13
MIN_SEKCJA_SPRAWOZDANIA = 30  # min. znaków na sekcję Zał. 7
DOZWOLONE_OCENY = {'2', '3', '3.5', '4', '4.5', '5'}  # skala ocen 2–5


def efekty_pokryte_w_dzienniku(dziennik):
    """Zbiór kodów efektów (01..13) występujących w którymkolwiek wpisie dziennika."""
    covered = set()
    if not dziennik:
        return covered
    for w in dziennik.wpisy:
        for kod in (w.nr_efektow or '').replace(';', ',').split(','):
            kod = kod.strip()
            if kod:
                covered.add(kod)
    return covered


def count_working_days(start, end):
    """Liczba dni roboczych (pon–pt) w zakresie [start, end] włącznie."""
    days = 0
    d = start
    while d <= end:
        if d.weekday() < 5:  # 0=pon ... 4=pt
            days += 1
        d += timedelta(days=1)
    return days


def working_day_end(start, n):
    """Data, na którą wypada n-ty dzień roboczy licząc od (włącznie) start."""
    d = start
    count = 0
    while True:
        if d.weekday() < 5:
            count += 1
            if count == n:
                return d
        d += timedelta(days=1)


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
            "zal32_zgloszenie_zopz": i.zal32_zgloszenie_zopz,
            "zal32_bhp_zopz": i.zal32_bhp_zopz,
            "dziennik_zatwierdzony": i.dziennik_zatwierdzony,
            "zal4_zopz": i.zal4_zopz,
            "zal4_uopz": i.zal4_uopz,
            "zal3_strona2_zopz": i.zal3_strona2_zopz,
            "zal3_strona2_uopz": i.zal3_strona2_uopz,
            "zal7_student": i.zal7_student,
            "zal7_zopz": i.zal7_zopz,
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

    dni_robocze = count_working_days(data_od, data_do)
    if dni_robocze != WYMAGANE_DNI_ROBOCZE:
        sugg = working_day_end(data_od, WYMAGANE_DNI_ROBOCZE)
        r, j = _err(
            f'Praktyka musi obejmować dokładnie {WYMAGANE_DNI_ROBOCZE} dni roboczych (pon–pt) — '
            f'wybrany zakres ma {dni_robocze}. Dla rozpoczęcia '
            f'{data_od.strftime("%d.%m.%Y")} data zakończenia powinna wynosić '
            f'{sugg.strftime("%d.%m.%Y")}.')
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
            efekty_count = EfektFormularza.query.filter_by(id_formularza=id).count()
            suma_dni = db.session.query(
                db.func.coalesce(db.func.sum(HarmonogramPraktyki.planowana_liczba_dni), 0)
            ).filter(HarmonogramPraktyki.id_formularza == id).scalar()
            if efekty_count < 13 or suma_dni != 120:
                msg = 'Najpierw wypełnij Zał. 2a (13 efektów + harmonogram = 120 dni).'
                if data.get('redirect_to'):
                    flash(msg, 'danger')
                    return redirect(data.get('redirect_to'))
                return jsonify({"error": msg}), 403
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
            if not internship.zal2a_uopz:
                return jsonify({"error": "Zał. 2a musi być zatwierdzony przed wystawieniem skierowania."}), 403
            internship.zal31_dyrektor = True
        elif document_type == 'ZAL3_2_ZGLOSZENIE' and role == 'zopz':
            if not internship.zal31_dyrektor:
                return jsonify({"error": "Dyrektor musi najpierw wystawić skierowanie (Zał. 3.1)."}), 403
            internship.zal32_zgloszenie_zopz = True
        elif document_type == 'ZAL3_2_BHP' and role == 'zopz':
            if not internship.zal31_dyrektor:
                return jsonify({"error": "Dyrektor musi najpierw wystawić skierowanie (Zał. 3.1)."}), 403
            internship.zal32_bhp_zopz = True
        else:
            return jsonify({"error": "Brak uprawnień lub nieznany dokument w Fazie 1."}), 403

    elif internship.faza_procesu == 2:
        if document_type == 'DZIENNIK_GOTOWY' and role == 'zopz':
            dziennik = internship.dziennik
            wpisy_count = len(dziennik.wpisy) if dziennik else 0
            if wpisy_count < 120:
                msg = f'Dziennik niekompletny ({wpisy_count}/120) — student musi go najpierw wypełnić.'
                if data.get('redirect_to'):
                    flash(msg, 'danger')
                    return redirect(data.get('redirect_to'))
                return jsonify({"error": msg}), 403
            brakujace = sorted(WSZYSTKIE_EFEKTY - efekty_pokryte_w_dzienniku(dziennik))
            if brakujace:
                msg = ('Dziennik nie pokrywa wszystkich efektów uczenia się — '
                       f'brakuje: {", ".join(brakujace)}. Wszystkie 13 efektów (01–13) '
                       'muszą wystąpić we wpisach przed zatwierdzeniem.')
                if data.get('redirect_to'):
                    flash(msg, 'danger')
                    return redirect(data.get('redirect_to'))
                return jsonify({"error": msg}), 403
            internship.dziennik_zatwierdzony = True
            internship.liczba_dni_roboczych = 120
            if dziennik:
                dziennik.status = 'Completed'
        else:
            return jsonify({"error": "Brak uprawnień w Fazie 2."}), 403

    elif internship.faza_procesu == 3:
        if document_type == 'ZAL7_ZOPZ' and role == 'zopz':
            if not internship.zal7_student:
                msg = 'Student nie złożył jeszcze Sprawozdania (Zał. 7).'
                if data.get('redirect_to'):
                    flash(msg, 'danger')
                    return redirect(data.get('redirect_to'))
                return jsonify({"error": msg}), 403
            internship.zal7_zopz = True
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

    db.session.commit()
    flash('Zał. 2a zapisany. Sprawdź dane i podpisz dokument przyciskiem poniżej.', 'success')
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


@internships_bp.route('/<int:id>/zal7', methods=['POST'])
@login_required
def submit_zal7(id):
    """Student wypełnia i składa Sprawozdanie (Zał. 7). Po złożeniu → potwierdza ZOPZ."""
    internship = Internship.query.get_or_404(id)
    back = f'/auth/formularze/{id}/zal7'

    if current_user.role != 'student':
        flash('Sprawozdanie składa student.', 'danger')
        return redirect(back)

    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student or internship.id_studenta != student.id_studenta:
        flash('Brak autoryzacji do tego formularza.', 'danger')
        return redirect('/auth/dashboard')

    if internship.faza_procesu != 3:
        flash('Sprawozdanie jest dostępne dopiero w Fazie 3 (Podsumowanie).', 'danger')
        return redirect(back)

    if internship.zal7_student:
        flash('Sprawozdanie zostało już złożone.', 'danger')
        return redirect(back)

    data = request.form
    charakterystyka = data.get('charakterystyka_miejsca', '').strip()
    opis_prac = data.get('opis_i_analiza_prac', '').strip()
    samoocena = data.get('samoocena_kompetencji', '').strip()

    sekcje = {
        'I. Charakterystyka miejsca odbywania praktyki': charakterystyka,
        'II. Opis i analiza wykonywanych prac': opis_prac,
        'III. Wiedza i umiejętności uzyskane w trakcie praktyki (samoocena)': samoocena,
    }
    for nazwa, tekst in sekcje.items():
        if len(tekst) < MIN_SEKCJA_SPRAWOZDANIA:
            flash(f'Sekcja „{nazwa}" musi mieć minimum {MIN_SEKCJA_SPRAWOZDANIA} znaków.', 'danger')
            return redirect(back)

    sprawozdanie = Sprawozdanie.query.filter_by(id_formularza=id).first()
    if sprawozdanie:
        sprawozdanie.charakterystyka_miejsca = charakterystyka
        sprawozdanie.opis_i_analiza_prac = opis_prac
        sprawozdanie.samoocena_kompetencji = samoocena
    else:
        db.session.add(Sprawozdanie(
            id_formularza=id,
            charakterystyka_miejsca=charakterystyka,
            opis_i_analiza_prac=opis_prac,
            samoocena_kompetencji=samoocena,
        ))

    internship.zal7_student = True
    db.session.commit()
    flash('Sprawozdanie złożone i podpisane. Oczekuje na potwierdzenie przez ZOPZ.', 'success')
    return redirect(back)


def _get_or_create_karta(id_formularza):
    karta = KartaPraktyki.query.filter_by(id_formularza=id_formularza).first()
    if not karta:
        karta = KartaPraktyki(id_formularza=id_formularza)
        db.session.add(karta)
        db.session.flush()
    return karta


@internships_bp.route('/<int:id>/zal32/zopz', methods=['POST'])
@login_required
@role_required('zopz', 'administrator')
def submit_zal32_zopz(id):
    """Zał. 3.2 (strona 2) — zaświadczenie odbycia + ocena zakładowa (ZOPZ)."""
    internship = Internship.query.get_or_404(id)
    back = f'/auth/formularze/{id}/zal32'

    if internship.faza_procesu != 3:
        flash('Kartę (strona 2) wypełnia się dopiero w Fazie 3 (po praktyce).', 'danger')
        return redirect(back)
    if internship.zal3_strona2_zopz:
        flash('Część zakładowa Karty (strona 2) została już wypełniona.', 'danger')
        return redirect(back)

    data = request.form
    ocena = data.get('ocena_zopz_param', '').strip()
    opis = data.get('ocena_zopz_opis', '').strip()
    uwagi = data.get('uwagi_odbycie', '').strip()

    if ocena not in DOZWOLONE_OCENY:
        flash('Ocena parametryczna musi być w skali 2–5 (dozwolone: 2, 3, 3.5, 4, 4.5, 5).', 'danger')
        return redirect(back)
    if len(opis) < 10:
        flash('Ocena opisowa jest wymagana (min. 10 znaków).', 'danger')
        return redirect(back)

    karta = _get_or_create_karta(id)
    karta.uwagi_odbycie = uwagi
    karta.ocena_zopz_param = ocena
    karta.ocena_zopz_opis = opis
    internship.zal3_strona2_zopz = True
    internship.check_and_advance_phase()
    db.session.commit()
    flash('Zaświadczenie i ocena zakładowa (Zał. 3.2) zapisane.', 'success')
    return redirect(back)


@internships_bp.route('/<int:id>/zal32/uopz', methods=['POST'])
@login_required
@role_required('uopz', 'administrator')
def submit_zal32_uopz(id):
    """Zał. 3.2 (strona 2) — ocena uczelniana + ocena sprawozdania (UOPZ)."""
    internship = Internship.query.get_or_404(id)
    back = f'/auth/formularze/{id}/zal32'

    if internship.faza_procesu != 3:
        flash('Kartę (strona 2) wypełnia się dopiero w Fazie 3 (po praktyce).', 'danger')
        return redirect(back)
    if not internship.zal3_strona2_zopz:
        flash('Najpierw część zakładową Karty musi wypełnić ZOPZ.', 'danger')
        return redirect(back)
    if not internship.zal7_student:
        flash('Ocena sprawozdania wymaga złożonego Sprawozdania (Zał. 7) przez studenta.', 'danger')
        return redirect(back)
    if internship.zal3_strona2_uopz:
        flash('Część uczelniana Karty (strona 2) została już wypełniona.', 'danger')
        return redirect(back)

    data = request.form
    ocena = data.get('ocena_uopz_param', '').strip()
    opis = data.get('ocena_uopz_opis', '').strip()
    ocena_spr = data.get('ocena_sprawozdania', '').strip()

    if ocena not in DOZWOLONE_OCENY or ocena_spr not in DOZWOLONE_OCENY:
        flash('Oceny parametryczne muszą być w skali 2–5 (dozwolone: 2, 3, 3.5, 4, 4.5, 5).', 'danger')
        return redirect(back)
    if len(opis) < 10:
        flash('Ocena opisowa jest wymagana (min. 10 znaków).', 'danger')
        return redirect(back)

    karta = _get_or_create_karta(id)
    karta.ocena_uopz_param = ocena
    karta.ocena_uopz_opis = opis
    karta.ocena_sprawozdania = ocena_spr
    internship.zal3_strona2_uopz = True
    internship.check_and_advance_phase()
    db.session.commit()
    flash('Ocena uczelniana i ocena sprawozdania (Zał. 3.2) zapisane.', 'success')
    return redirect(back)
