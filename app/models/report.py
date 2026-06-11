from app import db

class Sprawozdanie(db.Model):
    __tablename__ = 'sprawozdania'
    id_sprawozdania = db.Column(db.Integer, primary_key=True)
    id_formularza = db.Column(db.Integer, db.ForeignKey('formularze_praktyk.id_formularza'), unique=True, nullable=False)
    charakterystyka_miejsca = db.Column(db.Text, nullable=False)
    opis_i_analiza_prac = db.Column(db.Text, nullable=False)
    samoocena_kompetencji = db.Column(db.Text, nullable=False)
    formularz = db.relationship('Internship', backref=db.backref('sprawozdanie', uselist=False))
