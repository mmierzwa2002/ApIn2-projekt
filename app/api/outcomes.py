from flask import Blueprint, request, jsonify, abort
from flask_login import login_required
from app import db
from app.models.internship import Internship
from app.models.learning_outcome import LearningOutcome

VALID_OUTCOME_CODES = {str(i).zfill(2) for i in range(1, 14)}
VALID_STATUSES = {'Uzyskał', 'Nie uzyskał'}

outcomes_bp = Blueprint('outcomes', __name__, url_prefix='/api/outcomes')

@outcomes_bp.route('', methods=['GET'])
@login_required
def get_outcomes():
    internship_id = request.args.get('internship_id')
    query = LearningOutcome.query
    if internship_id:
        query = query.filter_by(internship_id=internship_id)

    outcomes = query.all()
    return jsonify([{
        "id": o.id,
        "praktyka_id": o.internship_id,
        "kod_efektu": o.outcome_code,
        "status": o.status
    } for o in outcomes]), 200

@outcomes_bp.route('', methods=['POST'])
@login_required
def create_outcome():
    data = request.get_json()
    if not data or not all(k in data for k in ('praktyka_id', 'kod_efektu', 'status')):
        abort(400, description="Brak wymaganych pól (praktyka_id, kod_efektu, status)")

    Internship.query.get_or_404(data['praktyka_id'], description="Praktyka nie istnieje")

    if data['kod_efektu'] not in VALID_OUTCOME_CODES:
        abort(400, description="Nieprawidłowy kod efektu. Dozwolone: 01-13")

    if data['status'] not in VALID_STATUSES:
        abort(400, description="Nieprawidłowy status. Dozwolone: 'Uzyskał', 'Nie uzyskał'")

    new_outcome = LearningOutcome(
        internship_id=data['praktyka_id'],
        outcome_code=data['kod_efektu'],
        status=data['status']
    )
    db.session.add(new_outcome)
    db.session.commit()
    return jsonify({"message": "Efekt kształcenia zapisany", "id": new_outcome.id}), 201

@outcomes_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_outcome(id):
    outcome = LearningOutcome.query.get_or_404(id)
    db.session.delete(outcome)
    db.session.commit()
    return jsonify({"message": "Efekt usunięty"}), 200
