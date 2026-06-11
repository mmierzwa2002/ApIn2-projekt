from app import db

class Student(db.Model):
    __tablename__ = 'studenci'
    id_studenta = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    imie = db.Column(db.String(50), nullable=False)
    nazwisko = db.Column(db.String(50), nullable=False)
    nr_albumu = db.Column(db.String(20), nullable=False, unique=True)
    kierunek = db.Column(db.String(100), nullable=False)
    specjalnosc = db.Column(db.String(100))
    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))

    @property
    def full_name(self):
        return f"{self.imie} {self.nazwisko}"
