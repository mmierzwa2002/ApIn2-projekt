from flask import Blueprint, request, jsonify, abort
from flask_login import login_required, current_user
from app.auth.decorators import role_required
from app import db
from app.models.user import User

students_bp = Blueprint('students', __name__, url_prefix='/api/students')

@students_bp.route('', methods=['GET'])
@login_required
@role_required('administrator', 'uopz', 'zopz', 'dyrektor')
def get_students():
    students = User.query.filter_by(role='student').all()
    return jsonify([{
        "id": s.id,
        "imie": s.full_name.split()[0] if s.full_name else "",
        "nazwisko": s.full_name.split()[-1] if s.full_name else "",
        "numer_indeksu": s.external_id,
        "email": s.email
    } for s in students]), 200

@students_bp.route('/<int:id>', methods=['GET'])
@login_required
@role_required('administrator', 'uopz', 'zopz', 'dyrektor')
def get_student(id):
    student = User.query.filter_by(id=id, role='student').first_or_404()
    return jsonify({
        "id": student.id,
        "imie": student.full_name.split()[0],
        "nazwisko": student.full_name.split()[-1],
        "numer_indeksu": student.external_id,
        "email": student.email
    }), 200

@students_bp.route('', methods=['POST'])
@login_required
@role_required('administrator', 'dyrektor')
def create_student():
    data = request.get_json()
    if not data or not all(k in data for k in ("imie", "nazwisko", "numer_indeksu", "email")):
        abort(400, description="Brak wymaganych danych (imie, nazwisko, numer_indeksu, email)")
    
    new_student = User(
        email=data['email'],
        full_name=f"{data['imie']} {data['nazwisko']}",
        external_id=data['numer_indeksu'],
        role='student'
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"message": "Student utworzony", "id": new_student.id}), 201

@students_bp.route('/<int:id>', methods=['PUT'])
@login_required
@role_required('administrator', 'dyrektor')
def update_student(id):
    student = User.query.filter_by(id=id, role='student').first_or_404()
    data = request.get_json()
    
    if 'imie' in data and 'nazwisko' in data:
        student.full_name = f"{data['imie']} {data['nazwisko']}"
    if 'email' in data:
        student.email = data['email']
    if 'numer_indeksu' in data:
        student.external_id = data['numer_indeksu']
        
    db.session.commit()
    return jsonify({"message": "Student zaktualizowany"}), 200

@students_bp.route('/<int:id>', methods=['DELETE'])
@login_required
@role_required('administrator')
def delete_student(id):
    student = User.query.filter_by(id=id, role='student').first_or_404()
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student usunięty"}), 200