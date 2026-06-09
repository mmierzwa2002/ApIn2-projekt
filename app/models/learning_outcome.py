from app import db

class LearningOutcome(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'), nullable=False)
    outcome_code = db.Column(db.String(2), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    internship = db.relationship('Internship', backref=db.backref('learning_outcomes', lazy=True))
