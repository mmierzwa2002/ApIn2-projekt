from app import db

class DziennikPraktyki(db.Model):
    __tablename__ = 'dzienniki_praktyk'
    id_dziennika = db.Column(db.Integer, primary_key=True)
    id_formularza = db.Column(db.Integer, db.ForeignKey('formularze_praktyk.id_formularza'), unique=True, nullable=False)
    status = db.Column(db.String(50), default='Draft')
    formularz = db.relationship('Internship', backref=db.backref('dziennik', uselist=False))

class WpisDziennika(db.Model):
    __tablename__ = 'wpisy_dziennika'
    id_wpisu = db.Column(db.Integer, primary_key=True)
    id_dziennika = db.Column(db.Integer, db.ForeignKey('dzienniki_praktyk.id_dziennika'), nullable=False)
    nr_dnia = db.Column(db.Integer)
    data_wpisu = db.Column(db.Date, nullable=False)
    opis_wykonanych_prac = db.Column(db.Text, nullable=False)
    id_efektu = db.Column(db.Integer, db.ForeignKey('efekty_ksztalcenia.id_efektu'))
    dziennik = db.relationship('DziennikPraktyki', backref=db.backref('wpisy', lazy=True))
    __table_args__ = (db.UniqueConstraint('id_dziennika', 'nr_dnia'),)
