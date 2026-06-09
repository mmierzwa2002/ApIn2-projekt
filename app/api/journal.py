from flask import Blueprint, request, jsonify, abort
from flask_login import login_required
from datetime import datetime
from app import db
from app.models.internship import Internship
from app.models.journal_entry import JournalEntry

journal_bp = Blueprint('journal', __name__, url_prefix='/api/journal')

@journal_bp.route('', methods=['GET'])
@login_required
def get_journal():
    internship_id = request.args.get('internship_id')
    query = JournalEntry.query
    if internship_id:
        query = query.filter_by(internship_id=internship_id)

    entries = query.all()
    return jsonify([{
        "id": e.id,
        "praktyka_id": e.internship_id,
        "data": e.date.strftime('%Y-%m-%d'),
        "godziny": e.hours,
        "opis": e.description
    } for e in entries]), 200

@journal_bp.route('', methods=['POST'])
@login_required
def create_journal_entry():
    data = request.get_json()
    if not data or not all(k in data for k in ('praktyka_id', 'data', 'godziny', 'opis')):
        abort(400, description="Brak wymaganych pól (praktyka_id, data, godziny, opis)")

    Internship.query.get_or_404(data['praktyka_id'], description="Praktyka nie istnieje")

    try:
        entry_date = datetime.strptime(data['data'], '%Y-%m-%d').date()
    except ValueError:
        abort(400, description="Nieprawidłowy format daty. Użyj YYYY-MM-DD")

    hours = int(data['godziny'])
    if hours < 1 or hours > 8:
        abort(400, description="Liczba godzin musi być między 1 a 8")

    new_entry = JournalEntry(
        internship_id=data['praktyka_id'],
        date=entry_date,
        hours=hours,
        description=data['opis']
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"message": "Wpis dodany do dziennika", "id": new_entry.id}), 201

@journal_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_journal_entry(id):
    entry = JournalEntry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Wpis usunięty"}), 200
