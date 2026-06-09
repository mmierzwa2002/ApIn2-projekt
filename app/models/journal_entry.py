from app import db
from datetime import date

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    internship = db.relationship('Internship', backref=db.backref('journal_entries', lazy=True))
