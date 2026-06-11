from app import db

class EfektKsztalcenia(db.Model):
    __tablename__ = 'efekty_ksztalcenia'
    id_efektu = db.Column(db.Integer, primary_key=True)
    kod = db.Column(db.String(2), nullable=False, unique=True)
    opis = db.Column(db.Text, nullable=False)

class EfektFormularza(db.Model):
    __tablename__ = 'efekty_formularza'
    id_formularza = db.Column(db.Integer, db.ForeignKey('formularze_praktyk.id_formularza'), primary_key=True)
    id_efektu = db.Column(db.Integer, db.ForeignKey('efekty_ksztalcenia.id_efektu'), primary_key=True)
    opis_prac = db.Column(db.Text, nullable=False)
    efekt = db.relationship('EfektKsztalcenia')

class PotwierdzenieEfektu(db.Model):
    __tablename__ = 'potwierdzenia_efektow'
    id_potwierdzenia = db.Column(db.Integer, primary_key=True)
    id_formularza = db.Column(db.Integer, db.ForeignKey('formularze_praktyk.id_formularza'), nullable=False)
    id_efektu = db.Column(db.Integer, db.ForeignKey('efekty_ksztalcenia.id_efektu'), nullable=False)
    czy_uzyskany = db.Column(db.SmallInteger)  # 0 lub 1
    __table_args__ = (db.UniqueConstraint('id_formularza', 'id_efektu'),)
