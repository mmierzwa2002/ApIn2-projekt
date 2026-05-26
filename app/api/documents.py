from flask import Blueprint, request, jsonify, abort
from datetime import datetime
from app import db
from app.models.internship import Internship
from app.models.document import Document

documents_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

@documents_bp.route('', methods=['GET'])
def get_documents():
    internship_id = request.args.get('internship_id')
    query = Document.query
    if internship_id:
        query = query.filter_by(internship_id=internship_id)
        
    docs = query.all()
    return jsonify([{
        "id": d.id,
        "nazwa_dokumentu": d.name,
        "typ_dokumentu": d.doc_type,
        "data_przeslania": d.upload_date.strftime('%Y-%m-%d'),
        "identyfikator_praktyki": d.internship_id,
        "status_weryfikacji": d.status,
        "komentarz_opiekuna": d.reviewer_comment
    } for d in docs]), 200

@documents_bp.route('', methods=['POST'])
def create_document():
    data = request.get_json()
    Internship.query.get_or_404(data.get('identyfikator_praktyki'), description="Praktyka nie istnieje")
    
    new_doc = Document(
        name=data['nazwa_dokumentu'],
        doc_type=data['typ_dokumentu'],
        upload_date=datetime.utcnow(),
        internship_id=data['identyfikator_praktyki'],
        status='Weryfikacja',
        reviewer_comment=data.get('komentarz_opiekuna', '')
    )
    db.session.add(new_doc)
    db.session.commit()
    return jsonify({"message": "Dokument przesłany", "id": new_doc.id}), 201

@documents_bp.route('/<int:id>', methods=['DELETE'])
def delete_document(id):
    doc = Document.query.get_or_404(id)
    db.session.delete(doc)
    db.session.commit()
    return jsonify({"message": "Dokument usunięty"}), 200