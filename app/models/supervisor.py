from app import db

formularz_opiekunowie = db.Table(
    'formularz_opiekunowie',
    db.Column('id_formularza', db.Integer, db.ForeignKey('formularze_praktyk.id_formularza'), primary_key=True),
    db.Column('id_opiekuna', db.Integer, db.ForeignKey('opiekunowie.id_opiekuna'), primary_key=True),
)

class Opiekun(db.Model):
    __tablename__ = 'opiekunowie'
    id_opiekuna = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    imie = db.Column(db.String(50), nullable=False)
    nazwisko = db.Column(db.String(50), nullable=False)
    typ_opiekuna = db.Column(db.String(30), nullable=False)  # 'uczelniany' | 'zakladowy'
    user = db.relationship('User', backref=db.backref('opiekun_profile', uselist=False))
