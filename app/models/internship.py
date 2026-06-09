from app import db

class Internship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='Oczekująca')
    stage = db.Column(db.String(50), default='dyrektor_wysyla_wstepne')
    student = db.relationship('User', backref=db.backref('internships', lazy=True))