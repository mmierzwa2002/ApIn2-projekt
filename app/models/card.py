from app import db

class KartaPraktyki(db.Model):
    __tablename__ = 'karty_praktyki'
    id_karty = db.Column(db.Integer, primary_key=True)
    id_formularza = db.Column(db.Integer, db.ForeignKey('formularze_praktyk.id_formularza'), unique=True, nullable=False)
    data_szkolenia_bhp = db.Column(db.Date)
    ocena_zakladowa = db.Column(db.Integer)    # Zał. 3.3/3.4 — ocena ZOPZ (2–5)
    ocena_uczelniana = db.Column(db.Integer)   # Zał. 3.5/3.6 — ocena UOPZ (2–5)
    data_podpisu = db.Column(db.Date)
    formularz = db.relationship('Internship', backref=db.backref('karta', uselist=False))
