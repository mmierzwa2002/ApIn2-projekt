from app import db
from datetime import datetime

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    doc_type = db.Column(db.String(100), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    internship_id = db.Column(db.Integer, db.ForeignKey('formularze_praktyk.id_formularza'), nullable=False)
    status = db.Column(db.String(50), default='Weryfikacja')
    reviewer_comment = db.Column(db.Text, nullable=True)
    internship = db.relationship('Internship', backref=db.backref('documents', lazy=True))