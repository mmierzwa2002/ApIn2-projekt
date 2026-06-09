from flask import Blueprint, request, jsonify, abort
from flask_login import login_required
from app.auth.decorators import role_required
from datetime import datetime
from app import db
from app.models.user import User
from app.models.internship import Internship 

internships_bp = Blueprint('internships', __name__, url_prefix='/api/internships')

@internships_bp.route('', methods=['GET'])
@login_required
def get_internships():
    student_id = request.args.get('student_id')
    query = Internship.query
    if student_id:
        query = query.filter_by(student_id=student_id)
        
    internships = query.all()
    return jsonify([{
        "id": i.id,
        "student_id": i.student_id,
        "nazwa_firmy": i.company_name,
        "data_rozpoczecia": i.start_date.strftime('%Y-%m-%d'),
        "data_zakonczenia": i.end_date.strftime('%Y-%m-%d'),
        "status": i.status
    } for i in internships]), 200

@internships_bp.route('', methods=['POST'])
@login_required
def create_internship():
    data = request.get_json()
    User.query.filter_by(id=data.get('student_id'), role='student').first_or_404(description="Student nie istnieje")
    
    start_date = datetime.strptime(data['data_rozpoczecia'], '%Y-%m-%d')
    end_date = datetime.strptime(data['data_zakonczenia'], '%Y-%m-%d')
    if start_date > end_date:
        abort(400, description="Data rozpoczęcia nie może być późniejsza niż data zakończenia")
        
    new_internship = Internship(
        student_id=data['student_id'],
        company_name=data['nazwa_firmy'],
        start_date=start_date,
        end_date=end_date,
        status=data.get('status', 'Oczekująca')
    )
    db.session.add(new_internship)
    db.session.commit()
    return jsonify({"message": "Praktyka utworzona", "id": new_internship.id}), 201

@internships_bp.route('/<int:id>', methods=['PUT', 'DELETE'])
@login_required
def modify_internship(id):
    from flask_login import current_user
    internship = Internship.query.get_or_404(id)
    
    if request.method == 'DELETE':
        if current_user.role != 'administrator':
            abort(403, description="Brak uprawnień do usuwania praktyk.")
            
        db.session.delete(internship)
        db.session.commit()
        return jsonify({"message": "Praktyka usunięta"}), 200
        
    if request.method == 'PUT':
        data = request.get_json()
        if 'status' in data:
            internship.status = data['status']
        db.session.commit()
        return jsonify({"message": "Status praktyki zaktualizowany"}), 200