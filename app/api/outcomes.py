from flask import Blueprint, request, jsonify, abort
from flask_login import login_required
from app import db
from app.models.internship import Internship
from app.models.outcome import EfektKsztalcenia, PotwierdzenieEfektu

outcomes_bp = Blueprint('outcomes', __name__, url_prefix='/api/outcomes')


@outcomes_bp.route('', methods=['GET'])
@login_required
def get_outcomes():
    internship_id = request.args.get('internship_id', type=int)
    query = PotwierdzenieEfektu.query
    if internship_id:
        query = query.filter_by(id_formularza=internship_id)
    outcomes = query.all()
    return jsonify([{
        "id": o.id_potwierdzenia,
        "id_formularza": o.id_formularza,
        "id_efektu": o.id_efektu,
        "czy_uzyskany": o.czy_uzyskany
    } for o in outcomes]), 200


@outcomes_bp.route('', methods=['POST'])
@login_required
def create_outcome():
    data = request.get_json()
    if not data or not all(k in data for k in ('id_formularza', 'id_efektu', 'czy_uzyskany')):
        abort(400, description="Wymagane pola: id_formularza, id_efektu, czy_uzyskany (0 lub 1)")

    Internship.query.get_or_404(data['id_formularza'], description="Formularz nie istnieje")
    EfektKsztalcenia.query.get_or_404(data['id_efektu'], description="Efekt kształcenia nie istnieje")

    if data['czy_uzyskany'] not in (0, 1):
        abort(400, description="czy_uzyskany musi być 0 lub 1")

    outcome = PotwierdzenieEfektu(
        id_formularza=data['id_formularza'],
        id_efektu=data['id_efektu'],
        czy_uzyskany=data['czy_uzyskany']
    )
    db.session.add(outcome)
    db.session.commit()
    return jsonify({"message": "Potwierdzenie efektu zapisane", "id": outcome.id_potwierdzenia}), 201


@outcomes_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_outcome(id):
    outcome = PotwierdzenieEfektu.query.get_or_404(id)
    db.session.delete(outcome)
    db.session.commit()
    return jsonify({"message": "Potwierdzenie usunięte"}), 200
