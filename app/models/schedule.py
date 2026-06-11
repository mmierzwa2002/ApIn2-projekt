from app import db

class HarmonogramPraktyki(db.Model):
    __tablename__ = 'harmonogram_praktyki'
    id_harmonogramu = db.Column(db.Integer, primary_key=True)
    id_formularza = db.Column(db.Integer, db.ForeignKey('formularze_praktyk.id_formularza'), nullable=False)
    lp = db.Column(db.Integer, nullable=False)
    dzial_komorka = db.Column(db.String(255), nullable=False)
    planowana_liczba_dni = db.Column(db.Integer, nullable=False)
    formularz = db.relationship('Internship', backref=db.backref('harmonogram', lazy=True))
    __table_args__ = (db.UniqueConstraint('id_formularza', 'lp'),)
