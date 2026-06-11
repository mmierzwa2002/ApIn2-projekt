from app import db

class Firma(db.Model):
    __tablename__ = 'firmy'
    id_firmy = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(255), nullable=False)
    adres = db.Column(db.String(255))
    przedstawiciel = db.Column(db.String(255))  # osoba uprawniona do reprezentacji
