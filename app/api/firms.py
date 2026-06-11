from flask import Blueprint, request, jsonify, redirect, flash
from flask_login import login_required
from app.auth.decorators import role_required
from app import db
from app.models.company import Firma

firms_bp = Blueprint('firms', __name__, url_prefix='/api/firms')


@firms_bp.route('', methods=['GET'])
@login_required
def get_firms():
    firms = Firma.query.order_by(Firma.nazwa).all()
    return jsonify([{
        'id': f.id_firmy,
        'nazwa': f.nazwa,
        'adres': f.adres,
        'przedstawiciel': f.przedstawiciel,
    } for f in firms])


@firms_bp.route('', methods=['POST'])
@login_required
@role_required('administrator', 'uopz')
def create_firm():
    is_form = bool(request.form)
    data = request.get_json(silent=True) or request.form

    nazwa = (data.get('nazwa') or '').strip()
    if not nazwa:
        if is_form:
            flash('Nazwa firmy jest wymagana.', 'danger')
            return redirect(data.get('redirect_to') or '/auth/dashboard')
        return jsonify({'error': 'Nazwa firmy jest wymagana'}), 400

    firma = Firma(
        nazwa=nazwa,
        adres=(data.get('adres') or '').strip() or None,
        przedstawiciel=(data.get('przedstawiciel') or '').strip() or None,
    )
    db.session.add(firma)
    db.session.commit()

    if is_form:
        flash(f'Dodano firmę: {firma.nazwa}', 'success')
        return redirect(data.get('redirect_to') or '/auth/dashboard')

    return jsonify({'id': firma.id_firmy, 'nazwa': firma.nazwa}), 201


@firms_bp.route('/<int:id>', methods=['DELETE'])
@login_required
@role_required('administrator', 'uopz')
def delete_firm(id):
    firma = Firma.query.get_or_404(id)
    db.session.delete(firma)
    db.session.commit()
    return jsonify({'message': 'Firma usunięta'}), 200
